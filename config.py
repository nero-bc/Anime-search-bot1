import os
import dotenv
from telethon import TelegramClient
from pymongo import MongoClient
from API.gogoanimeapi import Gogo
from pymongo.collection import Collection

dotenv.load_dotenv(".env")

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
db_url = os.environ.get('MONGO_DB_URL')
database_name = os.environ.get('DATABASE_NAME')
owner_id = int(os.environ.get('OWNER_ID'))
bot_username = os.environ.get('BOT_USERNAME')

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
client = MongoClient(db_url, tls=True)
data = Collection(client[database_name], 'ConfigDB').find_one({"_id": "GogoAnime"})

# Default values from environment variables
default_gogoanime_token = os.environ.get('DEFAULT_GOGOANIME_TOKEN', 'default_gogoanime_token')
default_auth_token = os.environ.get('DEFAULT_AUTH_TOKEN', 'default_auth_token')
default_url = os.environ.get('DEFAULT_URL', 'default_url')

gogoanime_token = data["gogoanime"] if data["gogoanime"] is not None else default_gogoanime_token
auth_token = data["auth"] if data["auth"] is not None else default_auth_token
host = data["url"] if data["url"] is not None else default_url

gogo = Gogo(
    gogoanime_token=gogoanime_token,
    auth_token=auth_token,
    host=host
)
