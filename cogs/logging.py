import discord
from discord.ext import commands

class CommandLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction, command):
        user = interaction.user
        cmd = command.qualified_name
        params = interaction.namespace.__dict__

        print(f"[COMMAND] {user} used /{cmd} with {params}")

async def setup(bot):
    await bot.add_cog(CommandLogger(bot))
