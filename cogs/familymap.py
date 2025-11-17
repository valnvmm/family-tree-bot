import discord
from discord.ext import commands
from discord import app_commands
from db import pool

import graphviz
import tempfile
import os


class FamilyMap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="familymap", description="Show all families in the server in one giant tree map.")
    async def familymap(self, interaction: discord.Interaction):

        await interaction.response.defer(thinking=True)

        async with pool.acquire() as con:
            users = await con.fetch("SELECT user_id, partner, parent1, parent2 FROM users")
            children = await con.fetch("SELECT parent, child FROM children")

        user_map = {row["user_id"]: row for row in users}

        parent_links = {}
        for row in children:
            parent = row["parent"]
            child = row["child"]
            parent_links.setdefault(parent, set()).add(child)

        partner_links = {}
        for row in users:
            if row["partner"]:
                partner_links[row["user_id"]] = row["partner"]

        dot = graphviz.Digraph(
            comment="Family Map",
            format="png",
            graph_attr={
                "rankdir": "TB",
                "splines": "true",
                "nodesep": "0.6",
                "ranksep": "0.9"
            },
            node_attr={
                "shape": "box",
                "style": "filled",
                "color": "#000000",
                "fontcolor": "white",
                "fontsize": "14",
                "penwidth": "1.5"
            },
            edge_attr={
                "penwidth": "1.2"
            }
        )

        for uid, row in user_map.items():
            user_obj = self.bot.get_user(uid)
            name = user_obj.display_name if user_obj else str(uid)
            dot.node(str(uid), name)

        for parent, kids in parent_links.items():
            for kid in kids:
                dot.edge(str(parent), str(kid), color="#FFFFFF")

        for uid, partner in partner_links.items():
            if partner in user_map:
                dot.edge(str(uid), str(partner), dir="none", color="#00A3FF", penwidth="2.0")

        # PURE PYTHON RENDERING — no `dot` needed
        rendered_bytes = dot.pipe(format="png")

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(rendered_bytes)
            temp_path = tmp.name

        await interaction.followup.send(
            content="📜 **Server Family Map** (Zoom in for details!)",
            file=discord.File(temp_path, filename="familymap.png")
        )

        os.remove(temp_path)


async def setup(bot):
    await bot.add_cog(FamilyMap(bot))
