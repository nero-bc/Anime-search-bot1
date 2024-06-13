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


async def send_download_link(client, message, id, ep_num):
    data = cdb.find({"_id": "GogoAnime"})
    gogo = Gogo(
        gogoanime_token=data["gogoanime"],
        auth_token=data["auth"],
        host=data["url"]
    )
    l1 = gogo.get_episodes_link(animeid=id, episode_num=ep_num)
    l2 = gogo.get_stream_link(animeid=id, episode_num=ep_num)
    r1 = format.format_download_results(l1)
    r2 = format.format_download_results(l2)
    await message.reply_text(
        f"Download Links for episode {ep_num}\n{r1}\n\nStreamable Links:\n{r2}"
    )


@app.on_callback_query(filters.regex("Download|longdl"))
async def callback_send_download_link(client, callback_query):
    data = callback_query.data.split(":")
    anime_id = data[1]
    episode_num = int(data[2])
    await send_download_link(client, callback_query.message, anime_id, episode_num)
