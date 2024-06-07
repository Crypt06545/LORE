import nextcord
import random
from nextcord.ext import commands
from nextcord import Interaction


class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # List of kick reasons
    kick_reasons = [
        "Breaking server rules",
        "Disruptive behavior",
        "Repeated violations",
        "Spamming"
    ]

    @nextcord.slash_command(name="kick", description="Kick a member from the server")
    async def kick_slash(self, interaction: Interaction, member: nextcord.Member, reason: str = None):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("This command requires `kick permission`", ephemeral=True)
            return

        if reason is None:
            reason = random.choice(self.kick_reasons)

        await member.kick(reason=reason)
        await interaction.response.send_message(f'{member.mention} has been kicked for: {reason}')

        # Send a direct message to the kicked member
        try:
            await member.send(f"You have been kicked 🦶 from **{interaction.guild.name}** for the **{reason}**")
        except nextcord.HTTPException:
            await interaction.response.send_message("Failed to send a direct message to the kicked member.", ephemeral=True)

