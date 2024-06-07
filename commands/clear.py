from nextcord.ext import commands
import nextcord

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="clear", description="Clear messages in the server")
    async def clear(self, interaction: nextcord.Interaction, amount: int = 11):
        if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
            await interaction.response.send_message("I need the `Manage Messages` permission to use this command.", delete_after=5)
            return

        if not interaction.user.guild_permissions.manage_messages:  # Check user's permissions
            await interaction.response.send_message("This command requires the `Manage Messages` permission.", delete_after=5)
            return

        amount = min(amount + 1, 101)  # Ensure amount is between 1 and 100
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message("Cleared messages", delete_after=5)  # Message will be deleted after 5 seconds
