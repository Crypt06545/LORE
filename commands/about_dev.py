from nextcord.ext import commands
import nextcord

class AboutDEV(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="aboutdev", description="Get information about the developer of this bot")
    async def slash_aboutdev(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="About the Developer",
            description="Here's some information about the developer of this bot!",
            color=0x3498db
        )

        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.add_field(name="Name", value="***MEHADI HASAN***", inline=False)
        embed.add_field(name="GitHub", value="[github.com/Crypt06545](https://github.com/Crypt06545)", inline=False)
        embed.add_field(name="Discord", value="```Crypt0◥▶_◀◤#4680```", inline=False)
        embed.add_field(name="Website", value="[mehadi.com](https://mehadi.onrender.com)", inline=False)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

        await interaction.response.send_message(embed=embed)

