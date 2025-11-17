import os
import asyncio
import datetime
from discord.ext import commands
import discord

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

TOKEN = os.getenv("DISCORD_TOKEN")

# ---------------------------------------------------------
# Load Cogs
# ---------------------------------------------------------
def load_cogs():
    log("Loading cogs...")
    for filename in os.listdir("./cogs"):
        if not filename.endswith(".py"):
            continue
        if filename == "__init__.py":
            continue

        name = filename[:-3]
        try:
            bot.load_extension(f"cogs.{name}")
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

    # Guilds
    log(f"Guilds loaded: {len(bot.guilds)}")

    # Cogs
    loaded = list(bot.cogs.keys())
    if loaded:
        log(f"Cogs active ({len(loaded)}): " + ", ".join(loaded))
    else:
        log("Warning: No cogs loaded.")

    # Database test
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
    load_cogs()
    log("Boot sequence complete. Running bot...")

    bot.run(TOKEN)
