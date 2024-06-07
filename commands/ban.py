import nextcord
import random
from nextcord.ext import commands


class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="ban", description="Ban from the server")
    async def ban(self, ctx: nextcord.Interaction, member: nextcord.Member, *, reason=None):
        if not ctx.user.guild_permissions.ban_members:
            await ctx.respond("This command requires ``ban permission``", ephemeral=True)
            return

        # List of ban reasons
        ban_reasons = [
            "Breaking server rules",
            "Spamming",
            "Disruptive behavior",
            "Toxicity"
        ]

        # Select a random reason if reason is not provided
        if reason is None:
            reason = random.choice(ban_reasons)

        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned by {ctx.user.mention} for: {reason}", ephemeral=True)
        # Adding reactions
        await ctx.channel.send(f"✅{member.mention} has been banned by {ctx.user.mention} for: {reason}")

        # Send a direct message to the banned member
        try:
            await member.send(f"You have been banned from **{ctx.guild.name}** for: {reason}")
        except nextcord.HTTPException:
            await ctx.respond("Failed to send a direct message to the banned member.", ephemeral=True)
