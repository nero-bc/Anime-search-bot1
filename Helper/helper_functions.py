@app.on_message(filters.command(["anime"]))
async def event_handler_anime(client, message):
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
        search_result = gogo.get_search_results(anime_name)
        try:
            (names, ids) = format.format_search_results(search_result)
            buttons = []
            for i in range(len(names)):
                buttons.append([InlineKeyboardButton(names[i], callback_data=f"dets:{ids[i]}")])
            await message.reply_text(
                'Search Results:',
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            await message.reply_text(
                'Not Found, Check for Typos or search Japanese name',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Example", url="https://media.giphy.com/media/4pk6ba2LUEMi4/giphy.gif")
                ]])
            )


@app.on_callback_query(filters.regex("dets:"))
async def callback_for_details(client, callback_query):
    data = callback_query.data
    id = data.split(":")[1]  # Extracting the ID from the callback data
    await send_details(client, callback_query, id)
