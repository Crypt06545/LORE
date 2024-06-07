from nextcord.ext import commands
import nextcord

class Avatar (commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="avatar", description="Get the avatar of a user")
    async def avatar(self,ctx, member: nextcord.Member = None):
        if member == None:
            member = ctx.user
        memberAvatar = member.avatar.url
        avaEmbed = nextcord.Embed(title = f"{member.name}'s Avatar")
        avaEmbed.set_image(url= memberAvatar)
        await ctx.send(embed = avaEmbed)
                                