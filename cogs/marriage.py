import discord
from discord.ext import commands
from discord import app_commands
from db import pool

GOLD = 0xC6A667

pending_requests = {}  # user_id → requester_id


class MarriageApproval(discord.ui.View):
    def __init__(self, requester_id, bot):
        super().__init__(timeout=60)
        self.requester_id = requester_id
        self.bot = bot

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_id = interaction.user.id
        requester = self.requester_id

        # Update DB
        async with pool.acquire() as con:
            await con.execute("""
                UPDATE users
                SET partner = $1
                WHERE user_id = $2
            """, requester, user_id)

            await con.execute("""
                UPDATE users
                SET partner = $1
                WHERE user_id = $2
            """, user_id, requester)

        # Notify requester
        try:
            usr = await self.bot.fetch_user(requester)
            await usr.send(f"💍 **{interaction.user.display_name}** accepted your proposal!")
        except:
            pass

        await interaction.response.edit_message(
            content="You accepted the marriage request! 💍",
            view=None
        )

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):

        requester = self.requester_id

        # Notify requester
        try:
            usr = await self.bot.fetch_user(requester)
            await usr.send(f"❌ **{interaction.user.display_name}** declined your marriage request.")
        except:
            pass

        await interaction.response.edit_message(
            content="You declined the marriage request.",
            view=None
        )


class Marriage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------------------------------------------------
    # /marry
    # ---------------------------------------------------------
    @app_commands.command(name="marry", description="Propose marriage to another user.")
    async def marry(self, interaction: discord.Interaction, user: discord.User):

        if user.id == interaction.user.id:
            return await interaction.response.send_message("❌ You cannot marry yourself.", ephemeral=True)

        # Check if either already married
        async with pool.acquire() as con:
            p1 = await con.fetchval("SELECT partner FROM users WHERE user_id=$1", interaction.user.id)
            p2 = await con.fetchval("SELECT partner FROM users WHERE user_id=$1", user.id)

        if p1:
            return await interaction.response.send_message("❌ You are already married.", ephemeral=True)
        if p2:
            return await interaction.response.send_message("❌ That user is already married.", ephemeral=True)

        # Send DM request
        try:
            await user.send(
                f"💍 **{interaction.user.display_name}** wants to marry you!",
                view=MarriageApproval(interaction.user.id, self.bot)
            )
        except:
            return await interaction.response.send_message(
                "❌ That user has closed DMs. Proposal failed.",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"📩 Marriage request sent to **{user.display_name}**!",
            ephemeral=True
        )

    # ---------------------------------------------------------
    # /divorce
    # ---------------------------------------------------------
    @app_commands.command(name="divorce", description="End your marriage.")
    async def divorce(self, interaction: discord.Interaction):

        user_id = interaction.user.id

        async with pool.acquire() as con:
            partner = await con.fetchval("SELECT partner FROM users WHERE user_id=$1", user_id)

            if not partner:
                return await interaction.response.send_message("❌ You are not married.", ephemeral=True)

            # Clear both
            await con.execute("UPDATE users SET partner=NULL WHERE user_id=$1", user_id)
            await con.execute("UPDATE users SET partner=NULL WHERE user_id=$1", partner)

        # Notify partner
        try:
            usr = await self.bot.fetch_user(partner)
            await usr.send(f"⚠️ **{interaction.user.display_name}** has divorced you.")
        except:
            pass

        await interaction.response.send_message(
            "💔 Your marriage has been dissolved.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Marriage(bot))
