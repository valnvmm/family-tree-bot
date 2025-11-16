import os
import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@tree.command(name="check", description="Check if the bot is online.")
async def check(interaction: discord.Interaction):
    await interaction.response.send_message("I'm online.")

TOKEN = os.getenv("1417955841352532049")

if not TOKEN:
    print("ERROR: No TOKEN environment variable found!")
else:
    bot.run(TOKEN)
