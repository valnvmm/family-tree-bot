import discord
from discord.ext import commands
from discord import app_commands
from db import pool


class Ancestor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ancestor", description="Find the earliest ancestor of a user.")
    async def ancestor(self, interaction: discord.Interaction, user: discord.User):

        await interaction.response.defer(thinking=True)

        async with pool.acquire() as con:
            current = user.id
            last_parent = None

            while True:
                row = await con.fetchrow("SELECT parent1, parent2 FROM users WHERE user_id=$1", current)
                if not row or (not row["parent1"] and not row["parent2"]):
                    break

                # pick any parent
                last_parent = row["parent1"] or row["parent2"]
                current = last_parent

        if last_parent is None:
            await interaction.followup.send(f"🧬 **{user.display_name}** has no known ancestors.")
        else:
            u = self.bot.get_user(last_parent)
            name = u.display_name if u else last_parent
            await interaction.followup.send(f"🧬 Earliest known ancestor of **{user.display_name}** is **{name}**.")


async def setup(bot):
    await bot.add_cog(Ancestor(bot))
