from pyrogram import Client as app, filters
from database import UsersDB
from config import bot_username
from Helper.helper import start_text, help_text

users = UsersDB()

#app = Client("my_bot")

@app.on_message(filters.command(["start", "start@" + bot_username]))
async def start_command(client, message):
    users.add({"_id": message.chat.id, "username": message.from_user.username, "name": f"{message.from_user.first_name} {message.from_user.last_name}"})
    await client.send_message(
        message.chat.id,
        start_text
        #file='https://tenor.com/view/chika-fujiwara-kaguya-sama-love-is-war-anime-wink-smile-gif-18043249'
    )

@app.on_message(filters.command(["help", "help@" + bot_username]))
async def help_command(client, message):
    await client.send_message(
        message.chat.id,
        help_text
    )

#if __name__ == '__main__':
    #app.run()
