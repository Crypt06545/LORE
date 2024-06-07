import nextcord
import random
import asyncio
from nextcord.ext import commands
from nextcord import Interaction


class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="mute", description="Mute a member in all voice channels")
    async def mute_slash(self, interaction: Interaction, member: nextcord.Member):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("This command requires `Manage Channels` permission", ephemeral=True)
            return

        # Acknowledge the command promptly
        await interaction.response.defer()

        reasons = [
            "Breaking server rules",
            "Spamming",
            "Disruptive behavior",
            "Ignoring warnings"
        ]

        reason = random.choice(reasons)

        voice_channels = interaction.guild.voice_channels
        tasks = []

        for channel in voice_channels:
            if member in channel.members:
                tasks.append(self.mute_member_in_channel(member, channel, reason))

        if tasks:
            await asyncio.gather(*tasks)
            await interaction.followup.send(f"{member.mention} has been muted for: {reason}")
            try:
                await member.send(f"You have been muted in all voice channels in **{interaction.guild.name}** for: {reason}")
            except nextcord.HTTPException:
                await interaction.followup.send("Failed to send a direct message to the muted member.", ephemeral=True)
        else:
            await interaction.followup.send(f"{member.mention} is not in any voice channels.")

    async def mute_member_in_channel(self, member, channel, reason):
        try:
            await member.edit(mute=True, reason=reason)
        except nextcord.Forbidden:
            print(f"Could not mute {member.display_name} in {channel.name} due to insufficient permissions.")


