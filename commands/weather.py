import nextcord
from nextcord.ext import commands
import aiohttp
import os


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="weather", description="Get the current weather for a specified city")
    async def weather(self, interaction: nextcord.Interaction, city: str):
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": os.getenv("API_KEY"),
            "q": city
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "error" in data:
                        await interaction.response.send_message(data["error"]["message"], ephemeral=True)
                    else:
                        location = data["location"]["name"]
                        country = data["location"]["country"]
                        temp_c = data["current"]["temp_c"]
                        condition_text = data["current"]["condition"]["text"]
                        icon = data["current"]["condition"]["icon"]
                        feelslike_c = data["current"]["feelslike_c"]
                        humidity = data["current"]["humidity"]
                        wind_kph = data["current"]["wind_kph"]
                        pressure_mb = data["current"]["pressure_mb"]
                        pressure_in = data["current"]["pressure_in"]

                        embed = nextcord.Embed(
                            title=f"Weather in {location}, {country}",
                            description=f"**{condition_text}**",
                            color=0x3498db
                        )
                        embed.set_thumbnail(url=f"https:{icon}")
                        embed.add_field(name="Temperature :thermometer:", value=f"{temp_c} °C", inline=True)
                        embed.add_field(name="Feels Like :hot_face:", value=f"{feelslike_c} °C", inline=True)
                        embed.add_field(name="Humidity :droplet:", value=f"{humidity}%", inline=True)
                        embed.add_field(name="Wind Speed :wind_blowing_face:", value=f"{wind_kph} km/h", inline=True)
                        embed.add_field(name="Pressure :arrow_up_down:", value=f"{pressure_mb} mb / {pressure_in} in", inline=True)
                        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

                        await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("An error occurred while fetching the weather data.", ephemeral=True)
