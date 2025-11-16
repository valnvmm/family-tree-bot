import discord
from discord.ext import commands
from discord import app_commands
from db import pool

pending_requests = {}  # target_user_id → requester_user_id

GOLD = 0xC6A667

class Marriage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="marry", description="Propose marriage to another user.")
    async def marry(self, interaction: discord.Interaction, user: discord.User):
        if user.id == interaction.user.id:
            return await interaction.response.send_message("You cannot marry yourself.", ephemeral=True)

        # Database checks
        async with pool.acquire() as con:
            partner = await con.fetchval("SELECT partner FROM users WHERE user_id=$1", interaction.user.id)
            user_partner = await con.fetchval("SELECT partner FROM users WHERE user_id=$1", user.id)

        if partner:
            return await interaction.response.send_message("You are already married.", ephemeral=True)

        if user_partner:
            return await interaction.response.send_message("That user is already married.", ephemeral=True)

        # Check pending requests
        if user.id in pending_requests:
            return await interaction.response.send_message(
                f"{user.mention} already has a pending marriage request.",
                ephemeral=True
            )

        pending_requests[user.id] = interaction.user.id

        embed = discord.Embed(
            title="Marriage Request Sent",
            description=f"{interaction.user.mention} has sent a marriage request to {user.mention}.",
            color=GOLD
        )
        await interaction.response.send_message(embed=embed)

        # Optional: Notify the target user directly
        try:
            await user.send(f"❤️ You received a marriage request from {interaction.user.mention}! Use `/acceptmarriage` to accept.")
        except:
            pass

    @app_commands.command(name="acceptmarriage", description="Accept the last received marriage request.")
    async def acceptmarriage(self, interaction: discord.Interaction):
        if interaction.user.id not in pending_requests:
            return await interaction.response.send_message("You have no pending marriage requests.", ephemeral=True)

        requester = pending_requests.pop(interaction.user.id)

        async with pool.acquire() as con:
            await con.execute("""
                INSERT INTO users(user_id, partner)
                VALUES($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET partner = EXCLUDED.partner;
            """, requester, interaction.user.id)

            await con.execute("""
                INSERT INTO users(user_id, partner)
                VALUES($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET partner = EXCLUDED.partner;
            """, interaction.user.id, requester)

        embed = discord.Embed(
            title="Marriage Confirmed",
            description=f"{interaction.user.mention} is now married to <@{requester}>.",
            color=GOLD
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="divorce", description="End your marriage.")
    async def divorce(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        async with pool.acquire() as con:
            partner = await con.fetchval("SELECT partner FROM users WHERE user_id=$1", user_id)

            if not partner:
                return await interaction.response.send_message("You are not married.", ephemeral=True)

            await con.execute("UPDATE users SET partner=NULL WHERE user_id=$1", user_id)
            await con.execute("UPDATE users SET partner=NULL WHERE user_id=$1", partner)

        embed = discord.Embed(
            title="Divorce Finalized",
            description="Your marriage has been peacefully dissolved.",
            color=GOLD
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Marriage(bot))
