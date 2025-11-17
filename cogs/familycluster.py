import discord
from discord.ext import commands
from discord import app_commands
from db import pool
import graphviz
import tempfile
import os


class FamilyCluster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def collect_family(self, user_id, parents, children):
        """Return all connected nodes (one family cluster)."""
        visited = set()
        queue = [user_id]

        while queue:
            u = queue.pop()
            if u in visited:
                continue
            visited.add(u)

            # parents
            for p in parents.get(u, []):
                if p not in visited:
                    queue.append(p)

            # children
            for c in children.get(u, []):
                if c not in visited:
                    queue.append(c)

        return visited

    @app_commands.command(name="familycluster", description="Show the user's family cluster as an image.")
    async def familycluster(self, interaction: discord.Interaction, user: discord.User):

        await interaction.response.defer(thinking=True)

        async with pool.acquire() as con:
            rows = await con.fetch("SELECT user_id, partner, parent1, parent2 FROM users")
            kid_rows = await con.fetch("SELECT parent, child FROM children")

        users = {r["user_id"]: r for r in rows}

        # Build parent/child maps
        parents = {}
        children = {}
        for r in kid_rows:
            parent = r["parent"]
            child = r["child"]
            parents.setdefault(child, []).append(parent)
            children.setdefault(parent, []).append(child)

        # Collect the cluster
        cluster = self.collect_family(user.id, parents, children)

        # Graphviz setup
        dot = graphviz.Digraph(format="png",
                               graph_attr={"rankdir": "TB"},
                               node_attr={"shape": "box", "style": "filled",
                                          "color": "#000", "fontcolor": "white"},
                               edge_attr={"color": "white"})

        # Add nodes
        for uid in cluster:
            uobj = self.bot.get_user(uid)
            name = uobj.display_name if uobj else str(uid)
            color = "#0077FF" if uid == user.id else "#000"
            dot.node(str(uid), name, color=color)

        # Add edges
        for r in kid_rows:
            if r["parent"] in cluster and r["child"] in cluster:
                dot.edge(str(r["parent"]), str(r["child"]))

        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "cluster")
            dot.render(out, cleanup=True)
            file = discord.File(out + ".png", filename="familycluster.png")

        await interaction.followup.send(
            content=f"📌 Family cluster for **{user.display_name}**",
            file=file
        )


async def setup(bot):
    await bot.add_cog(FamilyCluster(bot))
