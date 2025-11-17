import os
import asyncio
import datetime
from discord.ext import commands
import discord


print("🚀 Starting Family Tree Bot...")
import sys
print("Python version:", sys.version)
print("Loaded modules OK")

# ---------------------------------------------------------
# Logging helper
# ---------------------------------------------------------
def log(msg: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

# ---------------------------------------------------------
# Bot setup
# ---------------------------------------------------------
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# Use your Railway variable: DISCORD_TOKEN
from config import Config
TOKEN = Config.TOKEN


# ---------------------------------------------------------
# Load Cogs (async for discord.py 2.x)
# ---------------------------------------------------------
async def load_cogs():
    log("Loading cogs...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            name = filename[:-3]
            try:
                await bot.load_extension(f"cogs.{name}")
                log(f"  → Loaded cog: {name}")
            except Exception as e:
                log(f"  → Failed to load cog {name}: {e}")

# ---------------------------------------------------------
# Events
# ---------------------------------------------------------
@bot.event
async def on_ready():
    log("----------------------------------------")
    log("Starting FamilyTreeBot...")
    log(f"Logged in as: {bot.user} (ID: {bot.user.id})")
    log("----------------------------------------")

    log(f"Guilds loaded: {len(bot.guilds)}")

    loaded = list(bot.cogs.keys())
    if loaded:
        log(f"Cogs active ({len(loaded)}): " + ", ".join(loaded))
    else:
        log("Warning: No cogs loaded.")

    try:
        from db import get_db
        db = get_db()
        log("Database connection OK.")
    except Exception as e:
        log(f"Database connection FAILED: {e}")

    log("FamilyTreeBot is fully online.")
    log("----------------------------------------")

# ---------------------------------------------------------
# Startup
# ---------------------------------------------------------
if __name__ == "__main__":
    log("Boot sequence initiated...")

    async def main():
        await load_cogs()
        log("Boot sequence complete. Running bot...")

        await bot.start(TOKEN)

    asyncio.run(main())
