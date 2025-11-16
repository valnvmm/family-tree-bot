import discord
from discord.ext import commands
from discord import app_commands
from db import pool

GOLD = 0xC6A667


class AdoptionApprovalView(discord.ui.View):
    def __init__(self, parent_id, child_id, bot):
        super().__init__(timeout=60)
        self.parent_id = parent_id
        self.child_id = child_id
        self.bot = bot

    @discord.ui.button(label="Accept Adoption", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        # Add second parent
        async with pool.acquire() as con:
            await con.execute("""
                INSERT INTO children(parent, child)
                VALUES($1, $2)
                ON CONFLICT DO NOTHING;
            """, self.parent_id, self.child_id)

        parent_user = await self.bot.fetch_user(self.parent_id)
        child_user = interaction.user

        # Notify parent
        try:
            await parent_user.send(
                f"🎉 **{child_user.display_name}** has **accepted** your adoption request!"
            )
        except:
            pass

        # Update child's DM
        await interaction.response.edit_message(
            content="You accepted the adoption request! 🎉",
            view=None
        )

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):

        parent_user = await self.bot.fetch_user(self.parent_id)
        child_user = interaction.user

        # Notify parent
        try:
            await parent_user.send(
                f"❌ **{child_user.display_name}** has **declined** your adoption request."
            )
        except:
            pass

        # Update message
        await interaction.response.edit_message(
            content="You declined the adoption request.",
            view=None
        )


class Adoption(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="adopt", description="Ask to adopt another user.")
    async def adopt(self, interaction: discord.Interaction, user: discord.User):

        # Cannot adopt yourself
        if user.id == interaction.user.id:
            return await interaction.response.send_message(
                "You cannot adopt yourself.",
                ephemeral=True
            )

        # Check parent count
        async with pool.acquire() as con:
            parent_rows = await con.fetch(
                "SELECT parent FROM children WHERE child=$1",
                user.id
            )

        if len(parent_rows) >= 2:
            return await interaction.response.send_message(
                "❌ This user already has 2 parents.",
                ephemeral=True
            )

        # Prepare DM approval
        view = AdoptionApprovalView(
            parent_id=interaction.user.id,
            child_id=user.id,
            bot=self.bot
        )

        # Try sending DM to child
        try:
            await user.send(
                f"👶 **{interaction.user.display_name}** wants to adopt you!",
                view=view
            )
        except:
            return await interaction.response.send_message(
                "❌ This user has closed DMs. Adoption request failed.",
                ephemeral=True
            )

        # Confirm request sent
        await interaction.response.send_message(
            f"📩 Adoption request sent to **{user.display_name}**!",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Adoption(bot))
