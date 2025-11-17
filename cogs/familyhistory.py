import discord
from discord.ext import commands
from discord import app_commands
from db import pool
from datetime import datetime


class FamilyHistory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="familyhistory", description="Show a user's marriage and adoption history.")
    async def familyhistory(self, interaction: discord.Interaction, user: discord.User):

        await interaction.response.defer(thinking=True)

        async with pool.acquire() as con:
            marriages = await con.fetch("""
                SELECT user_a, user_b, married_at
                FROM marriages 
                WHERE user_a=$1 OR user_b=$1
                ORDER BY married_at ASC
            """, user.id)

            adoptions = await con.fetch("""
                SELECT parent, child 
                FROM children 
                WHERE parent=$1 OR child=$1
            """, user.id)

        embed = discord.Embed(
            title=f"Family History – {user.display_name}",
            color=0xC6A667
        )

        # Marriages
        if marriages:
            desc = ""
            for m in marriages:
                partner_id = m["user_b"] if m["user_a"] == user.id else m["user_a"]
                partner = self.bot.get_user(partner_id)
                pname = partner.display_name if partner else str(partner_id)

                desc += f"💍 Married to **{pname}** on `{m['married_at']}`\n"
            embed.add_field(name="Marriages", value=desc, inline=False)
        else:
            embed.add_field(name="Marriages", value="None", inline=False)

        # Adoptions
        if adoptions:
            desc = ""
            for a in adoptions:
                p = self.bot.get_user(a["parent"])
                c = self.bot.get_user(a["child"])
                pname = p.display_name if p else a["parent"]
                cname = c.display_name if c else a["child"]

                if a["parent"] == user.id:
                    desc += f"👶 Adopted **{cname}**\n"
                else:
                    desc += f"🧒 Adopted by **{pname}**\n"

            embed.add_field(name="Adoptions", value=desc, inline=False)
        else:
            embed.add_field(name="Adoptions", value="None", inline=False)

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(FamilyHistory(bot))
