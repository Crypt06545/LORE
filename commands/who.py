from nextcord.ext import commands
import nextcord
from datetime import datetime

class Who(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="who", description="Get information about a member")
    async def who(self, interaction: nextcord.Interaction, member: nextcord.Member):
        roles = [role for role in member.roles]

        embed = nextcord.Embed(title=f"Name: {member.name}",
                              description=member.mention, color=nextcord.Color.random(), timestamp=datetime.utcnow())

        embed.add_field(name="ID: ", value=member.id, inline=True)
        embed.add_field(name="Status", value=f"`{member.status}`", inline=True)
        embed.add_field(name="Activity", value=f"`{member.activity}`", inline=False)
        embed.add_field(name="Created Account On:", value=member.created_at.strftime(
            "%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
        embed.add_field(name="Joined Server On:", value=member.joined_at.strftime(
            "%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
        embed.add_field(name="Roles:", value="".join(
            [role.mention for role in roles]), inline=False)

        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(icon_url=interaction.user.avatar.url if interaction.user else nextcord.Embed.Empty,
                       text=f"Requested by {interaction.user.name if interaction.user else 'Unknown'}")
        return await interaction.response.send_message(embed=embed)
