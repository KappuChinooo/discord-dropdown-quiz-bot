import nextcord
from nextcord.ext.commands import Bot
from commands import dropdownGuessCog
import os
from dotenv import load_dotenv
from state import ChannelStateManager

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = [int(x) for x in os.getenv("GUILD_IDS", "").split(",") if x]
PREFIX = set([x for x in os.getenv("PREFIX", "!").split(",") if x])

intents = nextcord.Intents.default()
intents.message_content = True

state_manager = ChannelStateManager()

bot = Bot(command_prefix=PREFIX, intents=intents, default_guild_ids=GUILD_IDS)

bot.add_cog(dropdownGuessCog(bot, state_manager))

@bot.event
async def on_ready():
    print(f"logged in as: {bot.user}")
    for guild_id in GUILD_IDS:
        await bot.sync_application_commands(guild_id=guild_id)
        print(f"synced {guild_id}")

bot.run(TOKEN)
