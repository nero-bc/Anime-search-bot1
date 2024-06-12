from pyrogram import Client as app, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from API.Kissmangaapi import kissmangaapi as kiss
import Helper.formating_results as format
import os



@app.on_message(filters.command(["manga"]))
async def manga_search(client, message):
    if '/manga' == message.text:
        await message.reply_text(
            'Command must be used like this\n/manga <name of manga>\nexample: /manga One Piece',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Example", url="https://media1.tenor.com/images/eaac56a1d02536ed416b5a080fdf73ba/tenor.gif?itemid=15075442")
            ]])
        )
    else:
        manga_name = " ".join(message.text.split()[1:])
        results = kiss.get_search_results(manga_name)
        if len(results) == 0:
            await message.reply_text(
                'Not Found, Check for Typos or search Japanese name',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Example", url="https://media.giphy.com/media/4pk6ba2LUEMi4/giphy.gif")
                ]])
            )
        else:
            buttons = []
            for manga in results:
                buttons.append([InlineKeyboardButton(manga[0], callback_data=f"mid:{manga[1]}")])
            await message.reply_text(
                "Search Results:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

@app.on_message(filters.command(["read"]))
async def read_manga(client, message):
    try:
        manga_info = " ".join(message.text.split()[1:])
        manga_name, chapter_num = manga_info.split(":")
        chap = kiss.get_manga_chapter(manga_name, chapter_num)
        if chap == "Invalid Mangaid or chapter number":
            await message.reply_text("Something went wrong.....\nCheck if you entered command properly\nCommon mistakes:\nYou didnt mention chapter number\nyou added space after : , dont leave space")
            return
        f = format.manga_chapter_html(f"{manga_name} {chapter_num}", chap)
        await message.reply_text(
            "Open this in google chrome",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Chapter", url=f)
            ]])
        )
        os.remove(f)
    except Exception as e:
        await message.reply_text("Something went wrong.....\nCheck if you entered command properly\n\nUse /help if you have any doubts")
        print(e)

@app.on_message(filters.command(["rbatch"]))
async def read_batch(client, message):
    try:
        manga_info = " ".join(message.text.split()[1:])
        manga_id, start_ch, end_ch = manga_info.split(":")
        start_ch, end_ch = int(start_ch), int(end_ch)
        for i in range(start_ch, end_ch+1):
            chap = kiss.get_manga_chapter(manga_id, i)
            if chap == "Invalid Mangaid or chapter number":
                await message.reply_text("Something went wrong.....\nCheck if you entered command properly\nCommon mistakes:\nYou didnt mention chapter number\nyou added space after : , dont leave space")
                return
            f = format.manga_chapter_html(f"{manga_id}{i}", chap)
            await message.reply_text(
                "Open this in google chrome",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Chapter", url=f)
                ]])
            )
            os.remove(f)
    except Exception as e:
        await message.reply_text("Something went wrong.....\nCheck if you entered command properly\n\nUse /help if you have any doubts")
        print(e)

@app.on_callback_query(filters.regex("mid:"))
async def callback_for_mangadets(client, callback_query):
    data = callback_query.data[4:]
    txt, img = kiss.get_manga_details(data)
    await callback_query.edit_message_text(
        f"{txt}\n\n\nCopy This command and add chapter number at end\n\n`/read {data}:`",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Manga Details", url=img)
        ]])
    )
