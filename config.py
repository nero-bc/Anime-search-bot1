import os
import dotenv
from telethon import TelegramClient
from pymongo import MongoClient
from API.gogoanimeapi import Gogo
from pymongo.collection import Collection

class BotInitializer:
    def __init__(self):
        dotenv.load_dotenv(".env")
        self.api_id = int(os.environ.get('API_ID'))
        self.api_hash = os.environ.get('API_HASH')
        self.bot_token = os.environ.get('BOT_TOKEN')
        self.db_url = os.environ.get('MONGO_DB_URL')
        self.database_name = os.environ.get('DATABASE_NAME')
        self.owner_id = int(os.environ.get('OWNER_ID'))
        self.bot_username = os.environ.get('BOT_USERNAME')

        self.default_gogoanime_token = os.environ.get('DEFAULT_GOGOANIME_TOKEN', '58p11ds5010l3vbuoh9v46bm72')
        self.default_auth_token = os.environ.get('DEFAULT_AUTH_TOKEN', 'zrmZ1fem9erEK%2BbBQpSqldBcP0HJ8PxyIbDw3HWlCfiGe4kI3MVGq4tK6OGC3s0WdIqPGRP5FvmMsQvQWe8t6g%3D%3D')
        self.default_url = os.environ.get('DEFAULT_URL', 'anitaku.so')

        self.bot = None
        self.client = None
        self.data = None
        self.gogo = None

    def initialize_bot(self):
        self.bot = TelegramClient('bot', self.api_id, self.api_hash).start(bot_token=self.bot_token)

    def connect_to_database(self):
        self.client = MongoClient(self.db_url, tls=True)
        self.data = Collection(self.client[self.database_name], 'ConfigDB').find_one({"_id": "GogoAnime"})

    def initialize_gogo(self):
        if self.data:
            gogoanime_token = self.data.get("gogoanime", self.default_gogoanime_token)
            auth_token = self.data.get("auth", self.default_auth_token)
            host = self.data.get("url", self.default_url)
        else:
            gogoanime_token = self.default_gogoanime_token
            auth_token = self.default_auth_token
            host = self.default_url

        self.gogo = Gogo(
            gogoanime_token=gogoanime_token,
            auth_token=auth_token,
            host=host
        )

    def run(self):
        self.initialize_bot()
        self.connect_to_database()
        self.initialize_gogo()

if __name__ == "__main__":
    bot_initializer = BotInitializer()
    bot_initializer.run()
