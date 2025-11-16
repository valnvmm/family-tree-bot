import discord
from discord.ext import commands
from discord import app_commands
from db import pool

GOLD = 0xC6A667

class Family(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addchild", description="Add a child to your family.")
    async def addchild(self, interaction: discord.Interaction, child: discord.User):
        user_id = interaction.user.id

        async with pool.acquire() as con:
            partner = await con.fetchval("SELECT partner FROM users WHERE user_id=$1", user_id)

        if not partner:
            return await interaction.response.send_message("You must be married to add children.", ephemeral=True)

        async with pool.acquire() as con:
            await con.execute("""
                INSERT INTO children(parent, child)
                VALUES($1, $2)
                ON CONFLICT DO NOTHING;
            """, user_id, child.id)

            await con.execute("""
                INSERT INTO children(parent, child)
                VALUES($1, $2)
                ON CONFLICT DO NOTHING;
            """, partner, child.id)

            await con.execute("""
                INSERT INTO users(user_id)
                VALUES($1)
                ON CONFLICT DO NOTHING;
            """, child.id)

            # Set parents
            await con.execute("""
                UPDATE users SET parent1=$1, parent2=$2
                WHERE user_id=$3
            """, user_id, partner, child.id)

        embed = discord.Embed(
            title="Child Added",
            description=f"{child.mention} has been added to your family.",
            color=GOLD
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="familytree", description="Show a user's family tree.")
    async def familytree(self, interaction: discord.Interaction, user: discord.User = None):
        if user is None:
            user = interaction.user

        async with pool.acquire() as con:
            data = await con.fetchrow("""
                SELECT partner, parent1, parent2
                FROM users WHERE user_id=$1
            """, user.id)

            children = await con.fetch("""
                SELECT child FROM children WHERE parent=$1
            """, user.id)

        partner = f"<@{data['partner']}>" if data and data['partner'] else "None"
        parent1 = f"<@{data['parent1']}>" if data and data['parent1'] else "Unknown"
        parent2 = f"<@{data['parent2']}>" if data and data['parent2'] else "Unknown"
        kids = ", ".join(f"<@{c['child']}>" for c in children) if children else "None"

        text = f"""
┌── Parents ───────────────────┐
  {parent1}, {parent2}
└──────────────────────────────┘

┌── User ──────────────────────┐
  {user.mention}
└──────────────────────────────┘

┌── Partner ───────────────────┐
  {partner}
└──────────────────────────────┘

┌── Children ──────────────────┐
  {kids}
└──────────────────────────────┘
"""

        embed = discord.Embed(
            title="Family Tree",
            description=f"```\n{text}\n```",
            color=GOLD
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Family(bot))
