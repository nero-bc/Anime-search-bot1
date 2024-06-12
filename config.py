import os
import dotenv
from telethon import TelegramClient
from pymongo import MongoClient
from API.gogoanimeapi import Gogo
from pymongo.collection import Collection

dotenv.load_dotenv(".env")

API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
db_url = os.environ.get('MONGO_DB_URL')
database_name = os.environ.get('DATABASE_NAME')
owner_id = int(os.environ.get('OWNER_ID'))
bot_username = os.environ.get('BOT_USERNAME')

#bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
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

gogo = Gogo(
    gogoanime_token=gogoanime_token,
    auth_token=auth_token,
    host=host
)
