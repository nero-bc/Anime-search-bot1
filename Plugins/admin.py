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
        await message.reply_document("userdata.json", caption=f"Statistics for bot:\n Total number of users: {len(userdata)}")
        os.remove("userdata.json")
    else:
        await message.reply_text(f"Statistics for bot:\n Total number of users: {len(userdata)}")

@app.on_message(filters.command("broadcast") & filters.user(owner_id))
async def broadcast(client, message):
    msg = await message.reply_to_message()
    userdata = users.full()
    for i in userdata:
        try:
            await client.send_message(i['_id'], msg.text)
            await asyncio.sleep(0.5)
        except Exception as e:
            print(e)

@app.on_message(filters.command("update_token") & filters.user(owner_id))
async def update_token(client, message):
    if not message.reply_to_message or not message.reply_to_message.text:
        await message.reply_text("Please reply to a message containing the tokens and URL.")
        return

    msg = message.reply_to_message.text.split("\n")
    if len(msg) < 3:
        await message.reply_text("Invalid format. Please provide URL, auth token, and gogoanime token in the following format:\nURL\nauth_token\ngogoanime_token")
        return

    url = msg[0].strip()
    auth = msg[1].strip()
    gogoanime = msg[2].strip()

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

#if __name__ == "__main__":
   # bot.run()
