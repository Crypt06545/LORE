import nextcord
from nextcord.ext import commands
from PIL import Image
from io import BytesIO
import aiohttp
from dotenv import load_dotenv
import os
import asyncio  # new added

load_dotenv()
GUILD_ID = int(os.getenv("GUILD_ID"))

class ImageCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = asyncio.get_event_loop()  # ইভেন্ট লুপ নেওয়া
        self.session = aiohttp.ClientSession(loop=self.loop)  # লুপ পাস করা

    @nextcord.slash_command(name="wanted", description="Show a wanted poster for the specified user", guild_ids=[GUILD_ID])
    async def wanted(self, ctx, user: nextcord.Member = None):
        if user is None:
            user = ctx.user

        wanted = Image.open('images/wanted.jpg')

        avatar_url = user.avatar.url.replace('.webp', '.png')
        avatar_url = avatar_url + f"?size=128"

        async with self.session.get(avatar_url) as response:
            data = await response.read()

        pfp = Image.open(BytesIO(data))
        pfp = pfp.resize((320, 322))

        wanted.paste(pfp, (125, 256))

        profile_bytes = BytesIO()
        wanted.save(profile_bytes, format='JPEG')
        profile_bytes.seek(0)

        await ctx.response.send_message(file=nextcord.File(profile_bytes, filename='profile.jpg'))
        message = await ctx.original_message()

        await message.add_reaction("🤣")
        await message.add_reaction("😂")
        await message.add_reaction("😭")

def setup(bot):
    bot.add_cog(ImageCommands(bot))
