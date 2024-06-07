import nextcord
from nextcord.ext import commands
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor


class Waifus(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.executor = ThreadPoolExecutor()

    def fetch_waifu(self, tags, height=None):
        url = 'https://api.waifu.im/search'
        params = {
            'included_tags': tags
        }
        if height:
            params['height'] = height

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'images' in data and len(data['images']) > 0:
                return data['images'][0]['url']
        return None

    @nextcord.slash_command(
        name="anime_picture",
        description="Get anime pictures!"
    )
    async def anime(self, interaction: nextcord.Interaction, category: str):
        category_options = {
            "uniform": "uniform",
            "maid": "maid",
            "waifu": "waifu",
            "marin-kitagawa": "marin-kitagawa",
            "mori-calliope": "mori-calliope",
            "raiden-shogun": "raiden-shogun",
            "oppai": "oppai"
        }

        if category not in category_options:
            await interaction.response.send_message("Invalid category. Please choose from: uniform, maid, waifu, marin-kitagawa, mori-calliope, raiden-shogun, oppai")
            return

        tags = [category_options[category]]
        height = None
        if category in ["maid", "raiden-shogun"]:
            height = ">=2000"

        loop = asyncio.get_event_loop()
        url = await loop.run_in_executor(self.executor, self.fetch_waifu, tags, height)
        if url:
            await interaction.response.send_message(embed=nextcord.Embed().set_image(url=url))
        else:
            await interaction.response.send_message("Could not fetch image. Please try again later.")
