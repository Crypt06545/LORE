import nextcord
from nextcord.ext import commands
import asyncio

class On_Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)
        if isinstance(error, commands.errors.CommandNotFound):
            embed = nextcord.Embed(
                title="Invalid command",
                description="That command is not recognized",
                color=nextcord.Color.red()
            )
            msg = await ctx.send(embed=embed)
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            embed = nextcord.Embed(
                title="Missing argument",
                description="One or more required arguments are missing",
                color=nextcord.Color.red()
            )
            msg = await ctx.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title="❌Error",
                description=str(error),
                color=nextcord.Color.red()
            )
            msg = await ctx.send(embed=embed)

        # Delete the error message after 5 seconds
        await asyncio.sleep(5)
        await msg.delete()
