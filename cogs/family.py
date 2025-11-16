import discord
from discord.ext import commands
from discord import app_commands
from db import pool

GOLD = 0xC6A667


class Family(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------------------------------------------------
    # Helper: convert user ID → username, or placeholder
    # ---------------------------------------------------------
    async def resolve_name(self, user_id: int):
        if not user_id:
            return "Unknown"

        try:
            user = await self.bot.fetch_user(user_id)
            return user.display_name
        except:
            return f"<@{user_id}>"

    # ---------------------------------------------------------
    # /familytree command
    # ---------------------------------------------------------
    @app_commands.command(name="familytree", description="Show a user's family tree.")
    async def familytree(self, interaction: discord.Interaction, user: discord.User = None):

        target = user or interaction.user

        async with pool.acquire() as con:
            # Fetch parents + partner from users table
            row = await con.fetchrow(
                "SELECT parent1, parent2, partner FROM users WHERE user_id = $1",
                target.id
            )

            if row:
                parent1_id = row["parent1"]
                parent2_id = row["parent2"]
                partner_id = row["partner"]
            else:
                parent1_id = None
                parent2_id = None
                partner_id = None

            # Fetch children through the children table
            child_rows = await con.fetch(
                "SELECT child FROM children WHERE parent = $1",
                target.id
            )

        # Resolve names safely
        parent1 = await self.resolve_name(parent1_id)
        parent2 = await self.resolve_name(parent2_id)
        partner = await self.resolve_name(partner_id) if partner_id else "None"

        children = []
        for row in child_rows:
            children.append(await self.resolve_name(row["child"]))

        # Format children list
        children_text = ", ".join(children) if children else "None"

        # Build embed
        embed = discord.Embed(
            title=f"Family Tree — {target.display_name}",
            color=GOLD
        )

        embed.add_field(
            name="👨‍👩‍👧 Parents",
            value=f"{parent1}, {parent2}",
            inline=False
        )

        embed.add_field(
            name="🧍 User",
            value=target.display_name,
            inline=False
        )

        embed.add_field(
            name="❤️ Partner",
            value=partner,
            inline=False
        )

        embed.add_field(
            name="👶 Children",
            value=children_text,
            inline=False
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Family(bot))
