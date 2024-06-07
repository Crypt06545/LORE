import nextcord
from nextcord.ext import commands
from datetime import datetime


class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snipe_message_content = None
        self.snipe_message_author = None
        self.snipe_message_time = None
        self.snipe_message_delete_time = None

    @commands.Cog.listener()    
    async def on_message_delete(self, message):
        self.snipe_message_content = message.content
        self.snipe_message_author = message.author
        self.snipe_message_time = message.created_at
        self.snipe_message_delete_time = datetime.utcnow()

    @nextcord.slash_command(name="snipe", description="Retrieve the last deleted message")
    async def snipe(self, ctx: nextcord.Interaction):
        if self.snipe_message_content is None:
            await ctx.response.send_message("There's nothing to snipe!", ephemeral=True)
        else:
            embed = nextcord.Embed(
                description=self.snipe_message_content,
                color=nextcord.Color.red(),
                timestamp=self.snipe_message_delete_time
            )
            embed.set_author(name=f"**{self.snipe_message_author} deleted Message**:")

            embed.set_footer(text=f"Sent at {self.snipe_message_time.strftime('%a, %#d %B %Y, %I:%M %p %Z')} | Deleted at {self.snipe_message_delete_time.strftime('%a, %#d %B %Y, %I:%M %p %Z')}")

            await ctx.response.send_message(embed=embed)


