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
    print("🔧 Initializing database...")
    await init_db()

    print("🔧 Loading cogs...")
    await bot.load_extension("cogs.family")
    await bot.load_extension("cogs.marriage")
    await bot.load_extension("cogs.adoption")   # <-- MISSING

    print("🔗 Syncing commands...")
    await bot.tree.sync()

    print("✔️ Bot setup complete!")



@bot.event
async def on_ready():
    print(f"🚀 Bot online as {bot.user}")

bot.run(Config.TOKEN)
