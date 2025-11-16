import discord
from discord.ext import commands
from discord import app_commands
from db import pool

GOLD = 0xC6A667


# ============================================================
# Adoption DM View (Accept / Decline)
# ============================================================
class AdoptionApprovalView(discord.ui.View):
    def __init__(self, parent_id, child_id, bot):
        super().__init__(timeout=60)
        self.parent_id = parent_id
        self.child_id = child_id
        self.bot = bot

    # -----------------------------
    # Accept Adoption
    # -----------------------------
    @discord.ui.button(label="Accept Adoption", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        async with pool.acquire() as con:
            # Insert as second parent (or first)
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
                f"🎉 **{child_user.display_name}** has *accepted* your adoption request!"
            )
        except:
            pass

        # Update child message
        await interaction.response.edit_message(
            content="You accepted the adoption request! 🎉",
            view=None
        )

    # -----------------------------
    # Decline Adoption
    # -----------------------------
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):

        parent_user = await self.bot.fetch_user(self.parent_id)
        child_user = interaction.user

        # Notify parent
        try:
            await parent_user.send(
                f"❌ **{child_user.display_name}** has *declined* your adoption request."
            )
        except:
            pass

        await interaction.response.edit_message(
            content="You declined the adoption request.",
            view=None
        )


# ============================================================
# Adoption Commands Cog
# ============================================================
class Adoption(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------------------------------------------------
    # /adopt @user → request adoption
    # ---------------------------------------------------------
    @app_commands.command(name="adopt", description="Ask to adopt another user.")
    async def adopt(self, interaction: discord.Interaction, user: discord.User):

        parent_id = interaction.user.id
        child_id = user.id

        # Cannot adopt yourself
        if parent_id == child_id:
            return await interaction.response.send_message(
                "❌ You cannot adopt yourself.",
                ephemeral=True
            )

        # Limit: max 2 parents
        async with pool.acquire() as con:
            parent_rows = await con.fetch(
                "SELECT parent FROM children WHERE child = $1",
                child_id
            )

        if len(parent_rows) >= 2:
            return await interaction.response.send_message(
                "❌ This user already has **2 parents**.",
                ephemeral=True
            )

        # Prepare DM accept/decline
        view = AdoptionApprovalView(
            parent_id=parent_id,
            child_id=child_id,
            bot=self.bot
        )

        # Try DMing child
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

        await interaction.response.send_message(
            f"📩 Adoption request sent to **{user.display_name}**!",
            ephemeral=True
        )

    # ---------------------------------------------------------
    # /unadopt @child → parent removes child
    # ---------------------------------------------------------
    @app_commands.command(name="unadopt", description="Remove your parental link to a child.")
    async def unadopt(self, interaction: discord.Interaction, child: discord.User):

        parent_id = interaction.user.id
        child_id = child.id

        async with pool.acquire() as con:
            relation_exists = await con.fetchval(
                "SELECT 1 FROM children WHERE parent=$1 AND child=$2",
                parent_id, child_id
            )

            if not relation_exists:
                return await interaction.response.send_message(
                    "❌ You are not a parent of this child.",
                    ephemeral=True
                )

            await con.execute(
                "DELETE FROM children WHERE parent=$1 AND child=$2",
                parent_id, child_id
            )

        # Notify child via DM
        try:
            await child.send(
                f"⚠️ **{interaction.user.display_name}** has **unadopted you.**"
            )
        except:
            pass

        await interaction.response.send_message(
            f"✅ You have unadopted **{child.display_name}**.",
            ephemeral=True
        )

    # ---------------------------------------------------------
    # /runaway parent:@user → child runs away from one parent
    # ---------------------------------------------------------
    @app_commands.command(name="runaway", description="Run away from one of your parents.")
    async def runaway(self, interaction: discord.Interaction, parent: discord.User):

        child_id = interaction.user.id
        parent_id = parent.id

        async with pool.acquire() as con:
            relation_exists = await con.fetchval(
                "SELECT 1 FROM children WHERE parent=$1 AND child=$2",
                parent_id, child_id
            )

            if not relation_exists:
                return await interaction.response.send_message(
                    "❌ That user is not your parent.",
                    ephemeral=True
                )

            await con.execute(
                "DELETE FROM children WHERE parent=$1 AND child=$2",
                parent_id, child_id
            )

        # Notify parent via DM
        try:
            await parent.send(
                f"💨 **{interaction.user.display_name}** has run away from you."
            )
        except:
            pass

        await interaction.response.send_message(
            "💨 You have run away from that parent.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Adoption(bot))
