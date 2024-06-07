import nextcord
from nextcord.ext import commands
from PIL import Image
from io import BytesIO
import aiohttp




class ImageCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @nextcord.slash_command(name="wanted", description="Show a wanted poster for the specified user")
    async def wanted(self, ctx, user: nextcord.Member = None):
        if user is None:
            user = ctx.user

        wanted = Image.open('images/wanted.jpg')

        # Get the user's avatar URL with size (older method)
        avatar_url = user.avatar.url.replace('.webp', '.png')  # Replace .webp with .png if needed
        avatar_url = avatar_url + f"?size=128"  # Append size parameter

        async with self.session.get(avatar_url) as response:
            data = await response.read()

        pfp = Image.open(BytesIO(data))
        pfp = pfp.resize((320, 322))

        wanted.paste(pfp, (125, 256))

        profile_bytes = BytesIO()
        wanted.save(profile_bytes, format='JPEG')
        profile_bytes.seek(0)

        # Send the message and get the message ID
        await ctx.response.send_message(file=nextcord.File(profile_bytes, filename='profile.jpg'))
        message = await ctx.original_message()  # Fetch the original message

        # Add reaction to the message
        await message.add_reaction("🤣")
        await message.add_reaction("😂")
        await message.add_reaction("😭")

