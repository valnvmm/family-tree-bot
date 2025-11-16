import discord
from discord.ext import commands
from discord import app_commands
from db import pool

GOLD = 0xC6A667
pending_marriages = {}

class AcceptMarriage(discord.ui.View):
    def __init__(self, requester_id, target_id, bot):
        super().__init__(timeout=60)
        self.requester_id = requester_id
        self.target_id = target_id
        self.bot = bot

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with pool.acquire() as con:
            await con.execute("""
                INSERT INTO users(user_id, partner)
                VALUES($1,$2)
                ON CONFLICT (user_id) DO UPDATE SET partner=$2
            """, self.requester_id, self.target_id)
            await con.execute("""
                INSERT INTO users(user_id, partner)
                VALUES($1,$2)
                ON CONFLICT (user_id) DO UPDATE SET partner=$2
            """, self.target_id, self.requester_id)

        requester = await self.bot.fetch_user(self.requester_id)
        await requester.send(f"💍 Your marriage request to **{interaction.user.display_name}** was **accepted**!")

        await interaction.response.edit_message(
            content="You accepted the marriage request! ❤️",
            view=None
        )

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        requester = await self.bot.fetch_user(self.requester_id)
        await requester.send(f"❌ Your marriage request to **{interaction.user.display_name}** was **declined**.")

        await interaction.response.edit_message(
            content="You declined the marriage request.",
            view=None
        )

class Marriage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="marry", description="Propose marriage to another user.")
    async def marry(self, interaction: discord.Interaction, user: discord.User):
        view = AcceptMarriage(interaction.user.id, user.id, self.bot)

        try:
            await user.send(
                f"💍 **{interaction.user.display_name}** wants to marry you!",
                view=view
            )
        except:
            return await interaction.response.send_message("User has closed DMs!", ephemeral=True)

        await interaction.response.send_message("Marriage request sent!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Marriage(bot))
