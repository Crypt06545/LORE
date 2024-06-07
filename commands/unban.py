import nextcord
from nextcord.ext import commands


class UnBan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="unban", description="Unban from the server")
    async def unban(self, ctx: nextcord.Interaction, *, member):
        if not ctx.user.guild_permissions.ban_members:
            await ctx.send("This command needs `ban permission`")
            return

        banned_users = []  # Create an empty list to store banned users

        # Asynchronously iterate through the BanIterator and append users to the list
        async for entry in ctx.guild.bans():
            banned_users.append(entry.user)

        # Retrieve the banned user by comparing username
        banned_user = next((entry for entry in banned_users if entry.name.lower() == member.lower()), None)

        if banned_user:
            await ctx.guild.unban(banned_user)
            success_embed = nextcord.Embed(title="Unban Successful", description=f"✅ Unbanned {banned_user.name} by {ctx.user.mention}", color=0x00FF00)
            await ctx.send(embed=success_embed)
        else:
            await ctx.send(f'Member "{member}" not found in the ban list.')
