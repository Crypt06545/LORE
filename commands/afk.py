import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
import aiosqlite


class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.initialize_db())

    async def initialize_db(self):
        setattr(self.bot, "db", await aiosqlite.connect("db/main.db"))
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS afk (user INTEGER, guild INTEGER, reason TEXT)")
        await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT reason FROM afk WHERE user = ? AND guild = ?", (message.author.id, message.guild.id))
            data = await cursor.fetchone()
            if data:
                await message.channel.send(f"{message.author.mention} You are no longer AFK", delete_after=5)
                await cursor.execute("DELETE FROM afk WHERE user = ? AND guild = ?", (message.author.id, message.guild.id))
            
            if message.mentions:
                for mention in message.mentions:
                    await cursor.execute("SELECT reason FROM afk WHERE user = ? AND guild = ?", (mention.id, message.guild.id))
                    data2 = await cursor.fetchone()
                    if data2 and mention.id != message.author.id:
                        await message.channel.send(f"{mention.mention} is Currently AFK! Reason: `{data2[0]}`", delete_after=5)
        
        await self.bot.db.commit()
        await self.bot.process_commands(message)

    @nextcord.slash_command(name="afk", description="Set your AFK status")
    async def afk(self, interaction: Interaction, reason: str = SlashOption(description="The reason for being AFK", required=False, default="No Reason Provided")):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT reason FROM afk WHERE user = ? AND guild = ?", (interaction.user.id, interaction.guild.id))
            data = await cursor.fetchone()

            if data:
                if data[0] == reason:
                    return await interaction.response.send_message("You are already AFK with the same reason!", ephemeral=True)
                await cursor.execute("UPDATE afk SET reason = ? WHERE user = ? AND guild = ?", (reason, interaction.user.id, interaction.guild.id))
            else:
                await cursor.execute("INSERT INTO afk (user, guild, reason) VALUES (?, ?, ?)", (interaction.user.id, interaction.guild.id, reason))
        
        await self.bot.db.commit()
        await interaction.response.send_message(f"{interaction.user.mention} You are now AFK! Reason: `{reason}`", ephemeral=True)


