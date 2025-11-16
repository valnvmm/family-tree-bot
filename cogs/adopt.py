import discord
from discord.ext import commands
from discord import app_commands
from db import pool

GOLD = 0xC6A667


class AcceptAdoption(discord.ui.View):
    def __init__(self, parent_id, child_id, bot):
        super().__init__(timeout=60)
        self.parent_id = parent_id
        self.child_id = child_id
        self.bot = bot

    @discord.ui.button(label="Accept Adoption", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        # Create parent-child link
        async with pool.acquire() as con:
            await con.execute("""
                INSERT INTO children(parent, child)
                VALUES($1, $2)
                ON CONFLICT DO NOTHING;
            """, self.parent_id, self.child_id)

        parent = await self.bot.fetch_user(self.parent_id)
        child = interaction.user

        # DM parent
        try:
            await parent.send(f"👶 **{child.display_name}** has **accepted** your adoption request! ❤️")
        except:
            pass

        # Edit message
        await interaction.response.edit_message(
            content="You accepted the adoption request! 🎉",
            view=None
        )

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        parent = await self.bot.fetch_user(self.parent_id)
        child = interaction.user

        # DM parent
        try:
            await parent.send(f"❌ **{child.display_name}** has **declined** your adoption request.")
        except:
            pass

        await interaction.response.edit_message(
            content="You declined the adoption request.",
            view=None
        )


class Adoption(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="adopt", description="Request to adopt a user.")
    async def adopt(self, interaction: discord.Interaction, user: discord.User):

        # Cannot adopt yourself
        if user.id == interaction.user.id:
            return await interaction.response.send_message(
                "You cannot adopt yourself.", ephemeral=True
            )

        # Check if the child already has parents
        async with pool.acquire() as con:
            parent_rows = await con.fetch(
                "SELECT parent FROM children WHERE child=$1",
                user.id
            )

        if len(parent_rows) >= 2:
            return await interaction.response.send_message(
                "This user already has 2 parents.", ephemeral=True
            )

        # DM the child a confirmation
        view = AcceptAdoption(interaction.user.id, user.id, self.bot)

        try:
            await user.send(
                f"👶 **{interaction.user.display_name}** wants to adopt you!",
                view=view
            )
        except:
            return await interaction.response.send_message(
                "User has closed DMs. Adoption request failed.",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"Adoption request sent to {user.display_name}! 📩", ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Adoption(bot))
