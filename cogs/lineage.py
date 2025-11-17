import discord
from discord.ext import commands
from discord import app_commands
from db import pool


class Lineage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lineage", description="Show the direct lineage (ancestors) of a user.")
    async def lineage(self, interaction: discord.Interaction, user: discord.User):

        await interaction.response.defer(thinking=True)

        lineage = []
        current = user.id

        async with pool.acquire() as con:
            while True:
                row = await con.fetchrow("SELECT parent1, parent2 FROM users WHERE user_id=$1", current)
                if not row or (not row["parent1"] and not row["parent2"]):
                    break

                parent = row["parent1"] or row["parent2"]
                lineage.append(parent)
                current = parent

        if not lineage:
            await interaction.followup.send(f"📜 No lineage found for **{user.display_name}**.")
            return

        names = []
        for uid in lineage:
            u = self.bot.get_user(uid)
            names.append(u.display_name if u else str(uid))

        embed = discord.Embed(
            title=f"Lineage for {user.display_name}",
            description=" → ".join(names),
            color=0xC6A667
        )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Lineage(bot))
