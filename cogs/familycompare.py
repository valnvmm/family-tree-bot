import discord
from discord.ext import commands
from discord import app_commands
from db import pool


class FamilyCompare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="familycompare", description="Compare family connections between two users.")
    async def familycompare(self, interaction: discord.Interaction, user1: discord.User, user2: discord.User):

        await interaction.response.defer(thinking=True)

        async with pool.acquire() as con:
            one = await con.fetchrow("SELECT * FROM users WHERE user_id=$1", user1.id)
            two = await con.fetchrow("SELECT * FROM users WHERE user_id=$1", user2.id)

            kids1 = await con.fetch("SELECT child FROM children WHERE parent=$1", user1.id)
            kids2 = await con.fetch("SELECT child FROM children WHERE parent=$1", user2.id)

        embed = discord.Embed(
            title=f"Family Comparison",
            description=f"Comparing **{user1.display_name}** and **{user2.display_name}**",
            color=0xC6A667
        )

        # Partners
        if one and one["partner"] == user2.id:
            embed.add_field(name="Relationship", value="💍 They are **partners**.", inline=False)

        # Parents
        parents1 = {one["parent1"], one["parent2"]} if one else set()
        parents2 = {two["parent1"], two["parent2"]} if two else set()
        shared_parents = parents1.intersection(parents2)

        if shared_parents:
            plist = [self.bot.get_user(p).display_name for p in shared_parents if p]
            embed.add_field(name="Shared Parents", value=", ".join(plist), inline=False)

        # Children
        c1 = {k["child"] for k in kids1}
        c2 = {k["child"] for k in kids2}
        shared_kids = c1.intersection(c2)

        if shared_kids:
            klist = [self.bot.get_user(k).display_name for k in shared_kids]
            embed.add_field(name="Shared Children", value=", ".join(klist), inline=False)

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(FamilyCompare(bot))
