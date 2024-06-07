import nextcord
from nextcord.ext import commands

class Slowmo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="slowmode", description="Set slowmode for the channel")
    async def slowmode(self, interaction: nextcord.Interaction, time: int):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("This command requires `Manage Messages` permission.")
            return

        try:
            if time == 0:
                await interaction.channel.edit(slowmode_delay=0)
                await interaction.response.send_message('Slowmode turned off.')
            elif time > 21600:
                await interaction.response.send_message("You can't set the slowmode above 6 hours.")
            else:
                await interaction.channel.edit(slowmode_delay=time)
                await interaction.response.send_message(f'Slowmode set to {time} seconds!')
        except Exception:
            await interaction.response.send_message('Oops! Something went wrong.')


