import nextcord
from nextcord.ext import commands
import io
import os
import aiohttp

# AI ImageGenerations Class
class ImageGenerations(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.model_urls = {
            "openjourney-v4": "https://api-inference.huggingface.co/models/prompthero/openjourney-v4",
            "openjourney": "https://api-inference.huggingface.co/models/prompthero/openjourney",
            # "sdxl-turbo": "https://api-inference.huggingface.co/models/stabilityai/sdxl-turbo",
            "sdxl-flash": "https://api-inference.huggingface.co/models/sd-community/sdxl-flash",
            "stable-diffusion-2-1": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
            "stable-diffusion-xl-base-1.0": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            "omega-pony-anime-style-v2-sdxl": "https://api-inference.huggingface.co/models/John6666/omega-pony-anime-style-v2-sdxl"
        }

    # When the cog is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("ImageGenerations is online.")

    # Imagine command
    @nextcord.slash_command(
        name="imagine",
        description="Generate images using AI models"

    )
    async def imagine(
        self,
        interaction: nextcord.Interaction,
        model: str = nextcord.SlashOption(
            name="model",
            description="Choose the model",
            choices={
                "openjourney-v4", 
                "openjourney", 
                # "sdxl-turbo",
                "sdxl-flash",
                "stable-diffusion-xl-base-1.0", 
                "stable-diffusion-2-1",
            }
        ),
        prompt: str = nextcord.SlashOption(
            name="prompt",
            description="Describe the image you want to generate"
        )
    ):
        await interaction.response.defer()

        # Validate model input
        if model not in self.model_urls:
            await interaction.followup.send("Invalid model name.")
            return

        API_URL = self.model_urls[model]

        headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_TOKEN')}"}
        payload = {"inputs": f"{prompt}"}
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(API_URL, json=payload) as response:
                if response.status != 200:
                    error_message = await response.text()
                    await interaction.followup.send(f"Failed to generate image. Error: {error_message}")
                    return

                content_type = response.headers.get('Content-Type')
                if 'image' not in content_type:
                    error_message = await response.text()
                    await interaction.followup.send(f"Failed to generate image. Error: {error_message}")
                    return

                image_bytes = await response.read()
        
        with io.BytesIO(image_bytes) as file:  # converts to file-like object
            # Create an embed
            embed = nextcord.Embed(title=f"🎨 Generated Image by {interaction.user.display_name}")
            embed.add_field(name='📝 Prompt', value=f'- {prompt}', inline=False)
            embed.add_field(name='🤖 Model', value=f'- {model}', inline=True)
            embed.set_image(url="attachment://image.png")  # Set image URL in the embed

            # Send the embed with the image file
            await interaction.followup.send(
                embed=embed,
                file=nextcord.File(file, "image.png")
            )

    # Command to list available models
    @nextcord.slash_command(
        name="models",
        description="List available image generation models"
    )
    async def list_models(self, interaction: nextcord.Interaction):
        model_names = "\n".join(self.model_urls.keys())
        await interaction.response.send_message(f"Available models:\n{model_names}")

