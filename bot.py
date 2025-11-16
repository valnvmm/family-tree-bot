import discord
from discord.ext import commands
from config import Config
from db import init_db

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix="!", help_command=None)
tree = bot.tree

@bot.event
async def setup_hook():
    print("🔧 Database setup...")
    await init_db()
    await tree.sync()
    print("🔗 Slash commands synced.")

@bot.event
async def on_ready():
    print(f"🚀 Bot online as {bot.user}")

bot.run(Config.TOKEN)
