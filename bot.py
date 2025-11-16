import discord
from discord.ext import commands
from config import Config
from db import init_db

intents = discord.Intents.default()
bot = commands.Bot(intents=intents, command_prefix="!", help_command=None)
tree = bot.tree

@bot.event
async def on_ready():
    print(f"🚀 Bot online as {bot.user}")
    synced = await tree.sync()
    print(f"🔗 Synced {len(synced)} commands.")

@bot.event
async def setup_hook():
    await init_db()

bot.run(Config.TOKEN)
