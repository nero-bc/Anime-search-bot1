import os
import dotenv
from pymongo import MongoClient
from API.gogoanimeapi import Gogo
from pymongo.collection import Collection
from pyrogram import Client as PyrogramClient

dotenv.load_dotenv(".env")

api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
db_url = os.environ.get('MONGO_DB_URL')
database_name = os.environ.get('DATABASE_NAME')
owner_id = int(os.environ.get('OWNER_ID'))
bot_username = os.environ.get('BOT_USERNAME')

print(f"API_ID: {api_id}, API_HASH: {api_hash}, BOT_TOKEN: {bot_token}")

# Initialize the Pyrogram client correctly
bot = PyrogramClient('bot', api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Start the Pyrogram client
bot.start()

client = MongoClient(db_url, tls=True)
data = Collection(client[database_name], 'ConfigDB').find_one({"_id": "GogoAnime"})

# Default values from environment variables
default_gogoanime_token = os.environ.get('DEFAULT_GOGOANIME_TOKEN', '58p11ds5010l3vbuoh9v46bm72')
default_auth_token = os.environ.get('DEFAULT_AUTH_TOKEN', 'zrmZ1fem9erEK%2BbBQpSqldBcP0HJ8PxyIbDw3HWlCfiGe4kI3MVGq4tK6OGC3s0WdIqPGRP5FvmMsQvQWe8t6g%3D%3D')
default_url = os.environ.get('DEFAULT_URL', 'anitaku.so')

if data:
    gogoanime_token = data.get("gogoanime", default_gogoanime_token)
    auth_token = data.get("auth", default_auth_token)
    host = data.get("url", default_url)
else:
    gogoanime_token = default_gogoanime_token
    auth_token = default_auth_token
    host = default_url

print(f"GogoAnime Token: {gogoanime_token}, Auth Token: {auth_token}, URL: {host}")

gogo = Gogo(
    gogoanime_token=gogoanime_token,
    auth_token=auth_token,
    host=host
)



