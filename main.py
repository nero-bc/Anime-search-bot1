from telethon import TelegramClient, events
from Plugins.starter import Start
from Plugins.anime import Anime
from Plugins.manga import Manga
from Plugins.admin import Admin
from config import bot
import traceback

class Bot(TelegramClient):
    def init(self):
        super().__init__(
            "my_bot",
            bot.api_id,
            bot.api_hash,
            bot_token=bot.bot_token,
            workers=200,
            plugins={"root": "Plugins"},
            sleep_threshold=15,
        )
        self.start_plugin = Start()
        self.anime_plugin = Anime()
        self.manga_plugin = Manga()
        self.admin_plugin = Admin()

    async def start(self):
        await super().start()
        try:
            self.start_plugin
            self.anime_plugin
            self.manga_plugin
            self.admin_plugin
        except Exception:
            err_str = traceback.format_exc()
            print(err_str)
        print(f"{await self.get_me().first_name} is started...✨️")

    async def stop(self, *args):
        await super().stop()
        print("Bot stopped.")

if __name__ == "__main__":
    bot = Bot()
    bot.run_until_disconnected()
