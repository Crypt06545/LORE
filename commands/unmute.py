import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
from nextcord import Interaction

import asyncio


class UnMute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="unmute", description="Unmute a member in all voice channels")
    async def unmute(self, interaction: Interaction, member: nextcord.Member):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("This command requires `Manage Channels` permission", ephemeral=True)
            return

        # Acknowledge the command promptly
        await interaction.response.defer()

        voice_channels = interaction.guild.voice_channels
        tasks = []

        for channel in voice_channels:
            if member in channel.members:
                tasks.append(self.unmute_member_in_channel(member, channel))

        if tasks:
            await asyncio.gather(*tasks)
            await interaction.followup.send(f"{member.mention} has been unmuted.")
        else:
            await interaction.followup.send(f"{member.mention} is not currently muted in any voice channels.")

    async def unmute_member_in_channel(self, member, channel):
        try:
            await member.edit(mute=False, reason="Unmuting in voice channel")
        except nextcord.Forbidden:
            print(f"Could not unmute {member.display_name} in {channel.name} due to insufficient permissions.")

