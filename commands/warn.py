import nextcord
from nextcord.ext import commands
import aiosqlite


# ModWarn Class
class ModWarn(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("ModWarn is online.")

    # Warn command
    @nextcord.slash_command(name="warn", description="Warn a member.")
    async def warn(self, interaction: nextcord.Interaction, member: nextcord.Member, reason: str = None):
        # Check author role
        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message(f"Your role must be higher than {member.mention}.", ephemeral=True)
        # Check bot role
        if interaction.guild.me.top_role <= member.top_role:
            return await interaction.response.send_message(f"My role must be higher than {member.mention}.", ephemeral=True)
        if reason is None:
            reason = ""
        else:
            reason = f"\nReason: {reason}"
        # Add warn to database
        async with aiosqlite.connect("db/warnings.db") as db:  # Open the db
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS warnings (warns INTEGER, member INTEGER, guild ID)")
                await cursor.execute("SELECT warns FROM warnings WHERE member = ? AND guild = ?", (member.id, interaction.guild.id,))
                data = await cursor.fetchone()
                if data:
                    await cursor.execute("UPDATE warnings SET warns = ? WHERE member = ? AND guild = ?", (data[0] + 1, member.id, interaction.guild.id,))
                else:
                    await cursor.execute("INSERT INTO warnings (warns, member, guild) VALUES (?, ?, ?)", (1, member.id, interaction.guild.id,))
            await db.commit()
        warn_embed = nextcord.Embed(title="⚠️ ┃ Warn!", description=f"{member.mention} has been warned by {interaction.user.mention}{reason}", colour=nextcord.Colour.red())
        await interaction.response.send_message(embed=warn_embed)
    
    # Unwarn command
    @nextcord.slash_command(name="unwarn", description="Unwarn a member.")
    async def unwarn(self, interaction: nextcord.Interaction, member: nextcord.Member, amount: int = 1):
        # Check if member is the author
        if interaction.user == member:
            return await interaction.response.send_message("> You cannot unwarn yourself!", ephemeral=True)
        # Check author role
        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message(f"> Your role must be higher than {member.mention}!", ephemeral=True)
        # Check bot role
        if interaction.guild.me.top_role <= member.top_role:
            return await interaction.response.send_message(f"> My role must be higher than {member.mention}!", ephemeral=True)
        # Remove warning from database
        async with aiosqlite.connect("db/warnings.db") as db:  # Open the db
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS warnings (warns INTEGER, member INTEGER, guild ID)")
                await cursor.execute("SELECT warns FROM warnings WHERE member = ? AND guild = ?", (member.id, interaction.guild.id,))
                data = await cursor.fetchone()
                if data:
                    warns = data[0]
                    if warns - amount < 0:
                        return await interaction.response.send_message(f"{member.mention} has **{warns}** warnings only.", ephemeral=True)
                    elif warns - amount == 0:
                        await cursor.execute("DELETE FROM warnings WHERE member = ? AND guild = ?", (member.id, interaction.guild.id,))
                    else:
                        await cursor.execute("UPDATE warnings SET warns = ? WHERE member = ? AND guild = ?", (warns - amount, member.id, interaction.guild.id,))
                else:
                    return await interaction.response.send_message(f"{member.mention} doesn't have any warnings.", ephemeral=True)
            await db.commit()
        warn_embed = nextcord.Embed(title="✅ ┃ Unwarn!", description=f"**{amount}** warnings have been removed from {member.mention} by {interaction.user.mention}", colour=nextcord.Colour.green())
        await interaction.response.send_message(embed=warn_embed)

    # Warnings list command
    @nextcord.slash_command(name="warnings", description="Get list of warnings for the user.")
    async def warnings(self, interaction: nextcord.Interaction, member: nextcord.Member):
        async with aiosqlite.connect("db/warnings.db") as db:  # Open the db
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS warnings (warns INTEGER, member INTEGER, guild ID)")
                await cursor.execute("SELECT warns FROM warnings WHERE member = ? AND guild = ?", (member.id, interaction.guild.id,))
                data = await cursor.fetchone()
                if data:
                    await interaction.response.send_message(f"{member.mention} has **{data[0]}** warnings.")
                else:
                    await interaction.response.send_message(f"{member.mention} doesn't have any warnings.", ephemeral=True)
