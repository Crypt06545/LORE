import nextcord
from nextcord.ext import commands
from nextcord import Embed, Color
prefix = "/"

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    @nextcord.slash_command(
        name="help",
        description="Get help commands"
    )
    async def help(self, interaction: nextcord.Interaction):
        embed = Embed(title="**!Help commands**", color=Color.blue())
        embed.add_field(name="Ping :ping_pong:", value="Pings the bot and shows the response time\n> `/ping`", inline=True)
        embed.add_field(name="Who :mag_right:", value="See a member's information\n> `/who`", inline=True)
        embed.add_field(name="Ban :hammer:", value="Ban a user from the server\n> `/ban`", inline=True)
        embed.add_field(name="Memes :frame_photo:", value="See meme posts\n> `/memes`", inline=True)
        embed.add_field(name="Clear :wastebasket:", value="Clear the specified amount of messages\n> `/clear`", inline=True)
        embed.add_field(name="Ticket :ticket:", value="Create a support ticket\n> `/ticket`", inline=True)
        embed.add_field(name="Developer info :gear:", value="See info of the Bot Developer\n> `/aboutdev`", inline=True)
        embed.add_field(name="Weather :partly_sunny:", value="Shows the weather for the specified city\n> `/weather`", inline=True)
        embed.add_field(name="Avatar :frame_photo:", value="Shows the avatar of the specified user or yourself\n> `/avatar`", inline=True)
        embed.add_field(name="Snipe :mag:", value="Retrieve the last deleted message\n> `/snipe`", inline=True)
        embed.add_field(name="Level :star:", value="Shows your current level and experience points\n> `/level`", inline=True)
        embed.add_field(name="Mute :mute:", value="Mutes the specified user\n> `/mute`", inline=True)
        embed.add_field(name="Server info :bar_chart:", value="Shows information about the server\n> `/serverinfo`", inline=True)
        embed.add_field(name="Slowmode :turtle:", value="Sets the slowmode of the current channel\n> `/slowmode`", inline=True)
        embed.add_field(name="Unban :hammer_pick:", value="Unban a user from the server\n> `/unban`", inline=True)
        embed.add_field(name="Unmute :loud_sound:", value="Unmutes the specified user\n> `/unmute`", inline=True)
        embed.add_field(name="Anime :grinning:", value="Get random anime images or gifs\n> `/anime`", inline=True)
        
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.send(embed=embed)


