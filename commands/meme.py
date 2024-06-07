from nextcord.ext import commands
import nextcord
import requests
import json

class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="meme", description="For memes")
    async def meme(self, interaction: nextcord.Interaction):
        response = requests.get("https://meme-api.com/gimme").json()
        title = response['title']
        image_url = response['url']
        author = response['author']
        subreddit = response['subreddit']
        embed = nextcord.Embed(title=title, color=nextcord.Color.blue())
        embed.set_image(url=image_url)

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_message()

        await message.add_reaction("😂")
        await message.add_reaction("👍")
        await message.add_reaction("👎")