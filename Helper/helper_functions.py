import logging
from pyrogram import Client as app, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup,InputMediaPhoto
from Helper import formating_results as format
from database import ConfigDB
from API.gogoanimeapi import Gogo

cdb = ConfigDB()

PAGE_SIZE = 50
BUTTONS_PER_ROW = 4

async def send_details(client, event, id, page=1):
    data = cdb.find({"_id": "GogoAnime"})
    gogo = Gogo(
        gogoanime_token=data["gogoanime"],
        auth_token=data["auth"],
        host=data["url"]
    )
    if 'split:' in id:
        split_id = id.split(":")
        x = gogo.get_search_results(split_id[1])
        (_, ids) = format.format_search_results(x)
        for i in ids:
            if i[-25:] == split_id[2]:
                id = i
                break

    search_details = gogo.get_anime_details(id)
    genre = search_details.get('genres')
    episodes = search_details.get('episodes')
    title = search_details.get('title')
    other_names = search_details.get('other_names')
    year = search_details.get('year')
    status = search_details.get('status')
    season = search_details.get('season')
    img = search_details.get('image_url')
    text = f"""
<b>{title}</b>
{other_names}

<b>ID→</b> <code>{id}</code>
<b>Type→</b> {season}
<b>Status→</b> {status}
<b>Released→</b> {year}
<b>Episodes→</b> {episodes}
<b>Genres→</b> {genre}
"""
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    buttons = [
        InlineKeyboardButton(f"{i}", callback_data=f"Download:{id}:{i}")
        for i in range(start + 1, min(end + 1, episodes + 1))
    ]

    # Organize buttons into rows of BUTTONS_PER_ROW
    rows = [buttons[i:i + BUTTONS_PER_ROW] for i in range(0, len(buttons), BUTTONS_PER_ROW)]
    
    # Add pagination buttons if needed
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(InlineKeyboardButton("Previous", callback_data=f"Page:{id}:{page-1}"))
    pagination_buttons.append(InlineKeyboardButton(f"Page {page}", callback_data="noop"))
    if end < episodes:
        pagination_buttons.append(InlineKeyboardButton("Next", callback_data=f"Page:{id}:{page+1}"))
    rows.append(pagination_buttons)

    try:
        #await event.answer("please wait")
        """await event.edit_message_media(
            event.message.chat.id, 
            event.message.id, 
            InputMediaPhoto(img)
        )"""
        #await event.message.edit_text(
        await event.message.send_photo(img,
            text,
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode=enums.ParseMode.HTML
        )
        #await event.answer(MSG_ALRT)
        
        #await event.message.edit_text(
           # text,
            #reply_markup=InlineKeyboardMarkup(rows)
        #)
    except Exception as e:
        await event.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode=enums.ParseMode.HTML
        )


async def send_download_link(client, message, anime_id, episode_num):
    try:
        data = cdb.find({"_id": "GogoAnime"})
        gogo = Gogo(
            gogoanime_token=data["gogoanime"],
            auth_token=data["auth"],
            host=data["url"]
        )
        
        # Fetch download and stream links
        download_links = gogo.get_episodes_link(anime_id, episode_num)
        stream_links = gogo.get_stream_link(anime_id, episode_num)
        
        # Use the updated format_download_results function
        download_qualities, download_links = format.format_download_results(download_links)
        stream_qualities, stream_links = format.format_download_results(stream_links)
        
        # Debugging: print qualities and links
        logging.info(f"download_qualities: {download_qualities}")
        logging.info(f"download_links: {download_links}")
        logging.info(f"stream_qualities: {stream_qualities}")
        logging.info(f"stream_links: {stream_links}")

        if not stream_links and not download_links:
            await message.reply("No links found.")
            return

        buttons = []
        
        # Add stream links to buttons
        for i in range(len(stream_links)):
            try:
                text = stream_qualities[i]
                link = stream_links[i]
                # Check if the link is valid
                if link:
                    buttons.append([InlineKeyboardButton(f"Stream {text}", url=link)])
            except IndexError:
                logging.error(f"IndexError at i={i}, stream_qualities={stream_qualities}, stream_links={stream_links}")
                break  # Exit the loop if there's an IndexError
        
        # Add download links to buttons
        for i in range(len(download_links)):
            try:
                text = download_qualities[i]
                link = download_links[i]
                # Check if the link is valid
                if link:
                    buttons.append([InlineKeyboardButton(f"Download {text}", url=link)])
            except IndexError:
                logging.error(f"IndexError at i={i}, download_qualities={download_qualities}, download_links={download_links}")
                break  # Exit the loop if there's an IndexError

        # Send message with buttons
        await message.reply(
            text="Available Links:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        logging.error(f"An error occurred in send_download_link: {e}")

@app.on_callback_query(filters.regex("Download|longdl"))
async def callback_send_download_link(client, callback_query):
    data = callback_query.data.split(":")
    anime_id = data[1]
    episode_num = int(data[2])
    await send_download_link(client, callback_query.message, anime_id, episode_num)
