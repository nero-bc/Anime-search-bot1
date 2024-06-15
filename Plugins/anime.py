from pyrogram import Client as app, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from API.gogoanimeapi import Gogo
import Helper.formating_results as format
from database import ConfigDB
from Helper.helper_functions import *
import logging

logging.basicConfig(level=logging.INFO)
cdb = ConfigDB()

@app.on_message(filters.command(["latest"]))
async def event_handler_latest(client, message):
    try:
        data = cdb.find({"_id": "GogoAnime"})
        gogo = Gogo(
            gogoanime_token=data["gogoanime"],
            auth_token=data["auth"],
            host=data["url"]
        )
        home_page = gogo.get_home_page()
        (names, ids, epnums) = format.format_home_results(home_page)
        buttons = []
        for i in range(len(names)):
            buttons.append([InlineKeyboardButton(names[i], callback_data=f"lt:{ids[i]}")])
        await message.reply_text(
            'Latest anime added:',
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        logging.error(f"Error in latest: {e}")
        await message.reply_text("An error occurred while fetching the latest anime.")

@app.on_message(filters.command(["anime"]))
async def event_handler_anime(client, message):
    try:
        data = cdb.find({"_id": "GogoAnime"})
        gogo = Gogo(
            gogoanime_token=data["gogoanime"],
            auth_token=data["auth"],
            host=data["url"]
        )
        if '/anime' == message.text:
            await message.reply_text(
                'Command must be used like this\n/anime <name of anime>\nexample: /anime One Piece',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Example", url="https://media1.tenor.com/images/eaac56a1d02536ed416b5a080fdf73ba/tenor.gif?itemid=15075442")
                ]])
            )
        else:
            anime_name = " ".join(message.text.split()[1:])
            fetching_message = await message.reply_text('Fetching details...')
            search_result = gogo.get_search_results(anime_name)
            (names, ids) = format.format_search_results(search_result)
            buttons = []
            for i in range(len(names)):
                buttons.append([InlineKeyboardButton(names[i], callback_data=f"dts:{ids[i]}")])
            await fetching_message.edit_text(
                'Search Results:',
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        logging.error(f"Error in anime search: {e}")
        await fetching_message.edit_text(
            'Not Found, Check for Typos or search Japanese name',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Example", url="https://media.giphy.com/media/4pk6ba2LUEMi4/giphy.gif")
            ]])
        )

@app.on_callback_query(filters.regex("dts:"))
@app.on_callback_query(filters.regex("dts:"))
async def callback_for_details(client, callback_query):
    try:
        data = callback_query.data.split(":")
        anime_id = data[1]
        
        # Assuming you have the ConfigDB and Gogo instance accessible
        mak = cdb.find({"_id": "GogoAnime"})
        gogo = Gogo(
            gogoanime_token=mak["gogoanime"],
            auth_token=mak["auth"],
            host=mak["url"]
        )
        
        # Get anime details using gogo.get_anime_details(anime_id)
        search_details = gogo.get_anime_details(anime_id)
        
        # Format the details into text and buttons
        formatted_details = format.format_anime_details(search_details)
        genre = search_details.get('genres')
        episodes = search_details.get('episodes')
        title = search_details.get('title')
        other_names = search_details.get('other_names')
        year = search_details.get('year')
        status = search_details.get('status')
        season = search_details.get('season')
        img = search_details.get('image_url')
        
        if other_names and other_names.startswith("Other name:"):
            other_names = other_names.replace("Other name:", "").strip()

        text = f"""
        <b>{title}</b>
        {other_names}

        <b>ID→</b> <code>{anime_id}</code>
        <b>Type→</b> {season}
        <b>Status→</b> {status}
        <b>Released→</b> {year}
        <b>Episodes→</b> {episodes}
        <b>Genres→</b> {genre}
        """
        
        buttons = [
            [InlineKeyboardButton("Episodes", callback_data=f"dets:{anime_id}")],
            [InlineKeyboardButton("View on Web", url=search_details['url'])]
        ]
        
        await callback_query.message.reply_photo(
            photo=img,
            caption=text,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    except Exception as e:
        print(f"Error in callback_for_details: {e}")
        # Handle the error, perhaps send a message to the user indicating the error
        
    finally:
        # Always answer the callback query, even if an error occurs
        await callback_query.answer()

@app.on_message(filters.command(["batch"]))
async def event_handler_batch(client, message):
    try:
        if message.chat.id < 0:
            await message.reply("If you want to download in batch contact me in pm\n@Anime_Gallery_Robot")
            return
        anime_name = " ".join(message.text.split()[1:])
        split_data = anime_name.split(":")
        if int(split_data[2]) - int(split_data[1]) > 15:
            await message.reply(
                "Batch Download is capped at 15 episodes due to performance issues\nPlease download in batches of less than 15 for now"
            )
        else:
            for i in range(int(split_data[1]), (int(split_data[2]) + 1)):
                if await send_download_link(message, split_data[0], i) == False:
                    break
    except Exception as e:
        logging.error(f"Error in batch: {e}")
        await message.reply("Something went wrong.....\nCheck if you entered command properly\n\nUse /help if you have any doubts")

@app.on_message(filters.command(["download"]))
async def event_handler_download(client, message):
    try:
        data = cdb.find({"_id": "GogoAnime"})
        gogo = Gogo(
            gogoanime_token=data["gogoanime"],
            auth_token=data["auth"],
            host=data["url"]
        )
        anime_name = " ".join(message.text.split()[1:])
        split_data = anime_name.split(":")
        if int(split_data[2]) - int(split_data[1]) > 100:
            await message.reply(
                "Batch Download is capped at 100 episodes due to performance issues\nPlease download in batches of less than 100 for now"
            )
            return
        list_of_links = []
        await message.reply("Be Patient this is a slow process....")
        for i in range(int(split_data[1]), (int(split_data[2]) + 1)):
            list_of_links.append(gogo.get_episodes_link(split_data[0], i))
        format.batch_download_txt(split_data[0], list_of_links)
        await message.reply(
            "Import this file in **1DM** app.",
            file=f"{split_data[0]}.txt"
        )
    except Exception as e:
        logging.error(f"Error in download: {e}")
        await message.reply("Something went wrong.....\nCheck if you entered command properly\n\nUse /help if you have any doubts")

@app.on_callback_query(filters.regex("lt:"))
async def callback_for_latest(client, callback_query):
    try:
        data = callback_query.data
        id = data.split(":")[1]
        await send_details(callback_query, id)
    except Exception as e:
        logging.error(f"Error in callback_for_latest: {e}")
        await callback_query.message.reply_text("An error occurred while fetching details.")

@app.on_callback_query(filters.regex("Download"))
async def callback_for_download(client, callback_query):
    try:
        data = callback_query.data
        x = data.split(":")
        buttons = [[]]
        current_row = 0
        if int(x[2]) < 101:
            for i in range(int(x[2])):
                buttons[current_row].append(InlineKeyboardButton(str(i+1), callback_data=f'ep:{i+1}:{x[1]}'))
                if (i+1) % 5 == 0:
                    buttons.append([])
                    current_row += 1
        else:
            num_of_buttons = (int(x[2]) // 100)
            for i in range(num_of_buttons):
                buttons[current_row].append(InlineKeyboardButton(f'{i}01 - {i+1}00', callback_data=f'btz:{i+1}00:{x[1]}'))
                if (i+1) % 3 == 0:
                    buttons.append([])
                    current_row += 1
            if int(x[2]) % 100 != 0:
                buttons[current_row].append(InlineKeyboardButton(f'{num_of_buttons}01 - {x[2]}', callback_data=f'etz:{x[2]}:{x[1]}'))
                await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        logging.error(f"Error in callback_for_download: {e}")
        await callback_query.message.reply_text("An error occurred while processing your request.")

@app.on_callback_query(filters.regex("longdl"))
async def callback_for_download_long(client, callback_query):
    try:
        data = callback_query.data
        x = data.split(":")
        buttons = [[]]
        current_row = 0
        search_results = gogo.get_search_results(x[1])
        (names, ids) = format.format_search_results(search_results)
        for i in ids:
            if i[-25:] == x[2]:
                id = i
                break
        for i in range(int(x[3])):
            buttons[current_row].append(InlineKeyboardButton(str(i+1), callback_data=f'spp:{i+1}:{x[2]}:{x[1]}'))
            if (i+1) % 5 == 0:
                buttons.append([])
                current_row += 1
        await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        logging.error(f"Error in callback_for_download_long: {e}")
        await callback_query.message.reply_text("An error occurred while processing your request.")

@app.on_callback_query(filters.regex("btz:"))
async def callback_for_choosebuttons(client, callback_query):
    try:
        data = callback_query.data
        data_split = data.split(':')
        buttons = [[]]
        current_row = 0
        endnum = data_split[1]
        startnum = int(f'{int(endnum[0])-1}01')
        for i in range(startnum, (int(endnum)+1)):
            buttons[current_row].append(InlineKeyboardButton(str(i), callback_data=f'ep:{i}:{data_split[2]}'))
            if i % 5 == 0:
                buttons.append([])
                current_row += 1
        await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        logging.error(f"Error in callback_for_choosebuttons: {e}")
        await callback_query.message.reply_text("An error occurred while processing your request.")

@app.on_callback_query(filters.regex("etz:"))
async def callback_for_choosebuttons1(client, callback_query):
    try:
        data = callback_query.data
        data_split = data.split(':')
        buttons = [[]]
        current_row = 0
        endnum = int(data_split[1])
        startnum = int(f'{endnum//100}01')
        for i in range(startnum, (int(endnum)+1)):
            buttons[current_row].append(InlineKeyboardButton(str(i), callback_data=f'ep:{i}:{data_split[2]}'))
            if i % 5 == 0:
                buttons.append([])
                current_row += 1
        await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        logging.error(f"Error in callback_for_choosebuttons1: {e}")
        await callback_query.message.reply_text("An error occurred while processing your request.")

@app.on_callback_query(filters.regex("ep:"))
async def callback_for_downlink(client, callback_query):
    try:
        data = callback_query.data
        data_split = data.split(':')
        await send_download_link(callback_query, data_split[2], data_split[1])
    except Exception as e:
        logging.error(f"Error in callback_for_downlink: {e}")
        await callback_query.message.reply_text("An error occurred while processing your request.")

@app.on_callback_query(filters.regex("spp:"))
async def callback_for_downlink_long(client, callback_query):
    try:
        data = callback_query.data
        x = data.split(":")
        search_results = gogo.get_search_results(x[3])
        (names, ids) = format.format_search_results(search_results)
        for i in ids:
            if i[-25:] == x[2]:
                id = i
                break
        await send_download_link(callback_query, id, x[1])
    except Exception as e:
        logging.error(f"Error in callback_for_downlink_long: {e}")
        await callback_query.message.reply_text("An error occurred while processing your request.")

@app.on_callback_query(filters.regex("dets:|Page:"))
async def callback_for_details(client, callback_query):
    try:
        data = callback_query.data.split(":")
        anime_id = data[1]
        page = int(data[2]) if len(data) > 2 else 1
        await send_details(client, callback_query, anime_id, page)
    except Exception as e:
        logging.error(f"Error in callback_for_details: {e}")
        await callback_query.message.reply_text("An error occurred while fetching details.")

@app.on_callback_query(filters.regex("split:"))
async def callback_for_details_long(client, callback_query):
    try:
        data = callback_query.data
        id = data.split(":")[1]
        await send_details(callback_query, id)
    except Exception as e:
        logging.error(f"Error in callback_for_details_long: {e}")
        await callback_query.message.reply_text("An error occurred while fetching details.")
