from nextcord.ext import commands
import nextcord
import time
import psutil



class Ping (commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="ping", description="Ping the bot to check its responsiveness")
    async def ping(self,ctx):

        start_time = time.monotonic()
        msg = await ctx.send("📡 Pinging...")
        latency = (time.monotonic() - start_time) * 1000
        api_latency = round(self.bot.latency * 1000, 2)

        mem_used = psutil.Process().memory_full_info().rss / 1024 / 1024
        mem_total = psutil.virtual_memory().total / 1024 / 1024

        uptime = time.monotonic() - psutil.boot_time()
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)

        image_url = "https://avatars.githubusercontent.com/u/75322830"

        embed = nextcord.Embed(title="🏓 Pong!", color=0x3498db)
        embed.add_field(name="📡 Latency", value=f"{latency:.0f}ms", inline=True)
        embed.add_field(name="💻 API Latency", value=f"{api_latency:.0f}ms", inline=True)
        embed.add_field(name="💾 Memory Usage", value=f"{mem_used:.2f}/{mem_total:.2f} MB ({psutil.Process().memory_percent()}%)", inline=True)
        embed.add_field(name="⏳ Uptime", value=f"{int(hours)}h {int(minutes)}m {int(seconds)}s", inline=True)
        embed.set_thumbnail(url=image_url)


        await msg.edit(content=None, embed=embed)