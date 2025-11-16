import discord
from discord.ext import commands
from discord import app_commands
from db import pool

GOLD = 0xC6A667

class Family(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_name(self, user_id):
        try:
            user = await self.bot.fetch_user(user_id)
            return user.display_name
        except:
            return f"Unknown ({user_id})"

    def build_tree(self, parents, user_name, partner_name, children_names):
        """
        Bouwt een ASCII boomstructuur (Optie B)
        """

        def indent(lines, level=1):
            prefix = " " * 4 * level
            return "\n".join(prefix + line for line in lines.split("\n"))

        left_parent = parents[0] or "Unknown"
        right_parent = parents[1] or "Unknown"

        # Parent block
        parents_block = f"Parents\n├── {left_parent}\n└── {right_parent}"

        # User & Partner
        partner_block = (
            f"{user_name} ──┐\n"
            f"    ├── Partner: {partner_name}\n"
        )

        # Children block
        if children_names:
            child_lines = "\n".join([f"    └── Child: {c}" for c in children_names])
        else:
            child_lines = "    └── Child: None"

        return f"```\n{parents_block}\n\n{partner_block}{child_lines}\n```"

    @app_commands.command(name="familytree", description="Show a user's family tree.")
    async def familytree(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user

        async with pool.acquire() as con:
            parent_rows = await con.fetch("SELECT parent FROM children WHERE child=$1", user.id)
            parents = [None, None]
            for i, row in enumerate(parent_rows[:2]):
                parents[i] = await self.get_name(row["parent"])

            partner_id = await con.fetchval("SELECT partner FROM users WHERE user_id=$1", user.id)
            partner_name = await self.get_name(partner_id) if partner_id else "None"

            children_rows = await con.fetch("SELECT child FROM children WHERE parent=$1", user.id)
            children_names = [await self.get_name(r["child"]) for r in children_rows]

        user_name = await self.get_name(user.id)
        tree_text = self.build_tree(parents, user_name, partner_name, children_names)

        embed = discord.Embed(
            title="Family Tree",
            description=tree_text,
            color=GOLD
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Family(bot))
