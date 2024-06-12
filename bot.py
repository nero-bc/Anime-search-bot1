from pyrogram import Client
from pyrogram.enums import ParseMode

from config import api_id, api_hash, bot_token

#bot = Client('bot', api_id=APP_ID, api_hash=API_HASH, bot_token=TG_BOT_TOKEN)

name = """
░█████╗░░█████╗░██████╗░███████╗██╗░░██╗██████╗░░█████╗░████████╗███████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝██╔══██╗██╔══██╗╚══██╔══╝╚════██║
██║░░╚═╝██║░░██║██║░░██║█████╗░░░╚███╔╝░██████╦╝██║░░██║░░░██║░░░░░███╔═╝
██║░░██╗██║░░██║██║░░██║██╔══╝░░░██╔██╗░██╔══██╗██║░░██║░░░██║░░░██╔══╝░░
╚█████╔╝╚█████╔╝██████╔╝███████╗██╔╝╚██╗██████╦╝╚█████╔╝░░░██║░░░███████╗
░╚════╝░░╚════╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░░╚════╝░░░░╚═╝░░░╚══════╝
"""

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=api_id,
            api_id=api_hash,
            plugins={
                "root": "Plugins"
            },
            workers=4,
            bot_token=bot_token
        )

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.set_parse_mode(ParseMode.HTML)
        print(f"Bot Running..!\n\nCreated by \nhttps://t.me/CodeXBotz")
        print(name)

    async def stop(self, *args):
        await super().stop()
        print("Bot stopped.")

# Start the bot
#Bot().run()
