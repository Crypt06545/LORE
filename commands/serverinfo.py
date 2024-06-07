from nextcord.ext import commands
import nextcord
from nextcord import Interaction


class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="serverinfo", description="Display server information")
    async def serverinfo_slash(self, interaction: Interaction):
        role_count = len(interaction.guild.roles)
        list_of_bots = [bot.mention for bot in interaction.guild.members if bot.bot]

        serverinfoEmbed = nextcord.Embed(title=f"Server Information for {interaction.guild.name}", color=interaction.user.color, timestamp=interaction.created_at)
        
        serverinfoEmbed.set_thumbnail(url=interaction.guild.icon.url)

        serverinfoEmbed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        serverinfoEmbed.add_field(name="Admin", value=f'{interaction.guild.owner.name}')
        serverinfoEmbed.add_field(name='Member Count', value=f'{interaction.guild.member_count}', inline=True)
        serverinfoEmbed.add_field(name='Verification Level', value=str(interaction.guild.verification_level), inline=True)
        serverinfoEmbed.add_field(name='Highest Role', value=interaction.guild.roles[-2], inline=True)
        serverinfoEmbed.add_field(name='\u200b', value='\u200b', inline=False)
        serverinfoEmbed.add_field(name='Number of Roles', value=str(role_count), inline=True)
        serverinfoEmbed.add_field(name='\u200b', value='\u200b', inline=True)
        serverinfoEmbed.add_field(name='Bots', value=', '.join(list_of_bots), inline=True)
        serverinfoEmbed.set_footer(text=f"Server created at {interaction.guild.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC", icon_url=self.bot.user.avatar.url)
        await interaction.response.send_message(embed=serverinfoEmbed)
