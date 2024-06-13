import logging
from pyrogram import Client as app, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
    genre = search_details.get('genre')
    episodes = search_details.get('episodes')
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
        await event.message.edit_text(
            f"{search_details.get('title')}\nYear: {search_details.get('year')}\nStatus: {search_details.get('status')}\nGenre: {genre}\nEpisodes: {episodes}\nAnimeId: `{id}`",
            reply_markup=InlineKeyboardMarkup(rows)
        )
    except Exception as e:
        await event.message.edit_text(
            f"{search_details.get('title')}\nYear: {search_details.get('year')}\nStatus: {search_details.get('status')}\nGenre: {genre}\nEpisodes: {episodes}\nAnimeId: `{id}`",
            reply_markup=InlineKeyboardMarkup(rows)
        )


async def send_download_link(client, message, anime_id, episode_num):
    try:
        data = cdb.find({"_id": "GogoAnime"})
        gogo = Gogo(
            gogoanime_token=data["gogoanime"],
            auth_token=data["auth"],
            host=data["url"]
        )
        
        download_links = gogo.get_episodes_link(anime_id, episode_num)
        stream_links = gogo.get_stream_link(anime_id, episode_num)
        
        # Use the updated format_download_results function
        download_qualities, download_links = format_download_results(download_links)
        stream_qualities, stream_links = format_download_results(stream_links)
        
        # Debugging: print qualities and links
        logging.info(f"download_qualities: {download_qualities}")
        logging.info(f"download_links: {download_links}")
        logging.info(f"stream_qualities: {stream_qualities}")
        logging.info(f"stream_links: {stream_links}")

        if not stream_links:
            await message.reply("No stream links found.")
            return

        buttons = []
        for i in range(len(stream_links)):
            try:
                text = stream_qualities[i]
                link = stream_links[i]
                # Check if the link is valid
                if link:
                    buttons.append([InlineKeyboardButton(text, url=link)])
            except IndexError:
                logging.error(f"IndexError at i={i}, stream_qualities={stream_qualities}, stream_links={stream_links}")
                break  # Exit the loop if there's an IndexError

        # Send message with buttons
        await message.reply(
            text="Streamable Links:",
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
