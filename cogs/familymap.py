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
            # Fetch all table data
            users = await con.fetch("SELECT user_id, partner, parent1, parent2 FROM users")
            children = await con.fetch("SELECT parent, child FROM children")

        # Convert to dictionaries for easier mapping
        user_map = {row["user_id"]: row for row in users}

        # Build adjacency for parent → child
        parent_links = {}
        for row in children:
            parent = row["parent"]
            child = row["child"]
            parent_links.setdefault(parent, set()).add(child)

        # Build adjacency for partner links
        partner_links = {}
        for row in users:
            if row["partner"]:
                partner_links[row["user_id"]] = row["partner"]

        # Build DOT graph
        dot = graphviz.Digraph(
            comment="Family Map",
            format="png",
            graph_attr={
                "rankdir": "TB",      # Horizontal tree look
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

        # Add all users as nodes
        for uid, row in user_map.items():
            user_obj = self.bot.get_user(uid)
            name = user_obj.display_name if user_obj else str(uid)

            dot.node(str(uid), name)

        # Draw parent → child edges
        for parent, kids in parent_links.items():
            for kid in kids:
                dot.edge(str(parent), str(kid), color="#FFFFFF")

        # Draw partner ↔ partner edges (double-headed to look clean)
        for uid, partner in partner_links.items():
            if partner in user_map:  # safety to avoid broken refs
                dot.edge(str(uid), str(partner), dir="none", color="#00A3FF", penwidth="2.0")

        # Render graph to a temp file
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "familymap")
            dot.render(output_path, cleanup=True)
            png_path = output_path + ".png"

            # Send as Discord file
            file = discord.File(png_path, filename="familymap.png")

        await interaction.followup.send(
            content="📜 **Server Family Map**  
(Zoom in for details!)",
            file=file
        )


async def setup(bot):
    await bot.add_cog(FamilyMap(bot))
