from pyrogram import Client as app, filters
from database import UsersDB, ConfigDB
import json
import os
from config import owner_id
import asyncio

users = UsersDB()
cdb = ConfigDB()


@app.on_message(filters.command("stats") & filters.user(owner_id))
async def stats(client, message):
    userdata = users.full()
    if "export" in message.text:
        with open("userdata.json", "w") as final:
            json.dump(userdata, final, indent=4)
        await message.reply_text(f"Statistics for bot:\n Total number of users: {len(userdata)}", reply_markup="userdata.json")
        os.remove("userdata.json")
    else:
        await message.reply_text(f"Statistics for bot:\n Total number of users: {len(userdata)}")

@app.on_message(filters.command("broadcast") & filters.user(owner_id))
async def broadcast(client, message):
    msg = await message.reply_to_message()
    userdata = users.full()
    for i in userdata:
        try:
            await client.send_message(i['_id'], msg)
            await asyncio.sleep(0.5)
        except Exception as e:
            print(e)

@app.on_message(filters.command("update_token") & filters.user(owner_id))
async def update_token(client, message):
    msg = message.reply_to_message.text.split("\n")
    url = msg[0].split("	")[0]
    gogoanime = msg[1][6]
    auth = msg[0][6]

    cdb.modify(
        {
            "_id": "GogoAnime"
        },
        {
            "_id": "GogoAnime",
            "url": url,
            "gogoanime": gogoanime,
            "auth": auth
        }
    )

    await message.reply_text("Token Updated Successfully.")

