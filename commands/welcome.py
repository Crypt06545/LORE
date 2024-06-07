import nextcord
from nextcord.ext import commands
import aiosqlite
from dotenv import load_dotenv


class MemberEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ensure_db(self):
        async with aiosqlite.connect("db/welcome.db") as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS welcome (
                    guild_id INTEGER PRIMARY KEY, 
                    channel_id INTEGER, 
                    welcome_msg TEXT, 
                    bye_msg TEXT,
                    is_enabled INTEGER DEFAULT 1
                )
            """)
            await db.commit()

    async def get_welcome_settings(self, guild_id):
        async with aiosqlite.connect("db/welcome.db") as db:
            async with db.execute("SELECT channel_id, welcome_msg, bye_msg, is_enabled FROM welcome WHERE guild_id = ?", (guild_id,)) as cursor:
                return await cursor.fetchone()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.ensure_db()
        result = await self.get_welcome_settings(member.guild.id)

        if result:
            channel_id, welcome_msg, _, is_enabled = result
            if channel_id is not None and is_enabled:
                welcome_embed = nextcord.Embed(
                    title="Welcome To The Server!!!",
                    description=welcome_msg.format(member=member.mention) if welcome_msg else f"{member.mention} has joined the server 🎉🎉",
                    color=nextcord.Color.blue()
                )
                welcome_embed.set_thumbnail(url=str(member.avatar.url))
                await self.bot.get_channel(int(channel_id)).send(embed=welcome_embed)
            
            buddy_role = nextcord.utils.get(member.guild.roles, name="buddy")
            if not buddy_role:
                buddy_role = await member.guild.create_role(name="buddy")

            await member.add_roles(buddy_role)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.ensure_db()
        result = await self.get_welcome_settings(member.guild.id)

        if result:
            channel_id, _, bye_msg, is_enabled = result
            if channel_id is not None and is_enabled:
                farewell_embed = nextcord.Embed(
                    title="Has Left the server :(",
                    description=bye_msg.format(member=member.mention) if bye_msg else f"{member.mention} চলে গেস তাতে কি নতুন একটা পেয়ে যাব।😎",
                    color=nextcord.Color.red()
                )
                farewell_embed.set_thumbnail(url=str(member.avatar.url))
                await self.bot.get_channel(int(channel_id)).send(embed=farewell_embed)

    @nextcord.slash_command(name="set_welcome_channel", description="Set the welcome channel for the server.")
    @commands.has_permissions(manage_channels=True)
    async def set_welcome_channel(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel):
        await self.ensure_db()
        async with aiosqlite.connect("db/welcome.db") as db:
            await db.execute("INSERT OR REPLACE INTO welcome (guild_id, channel_id) VALUES (?, ?)", (interaction.guild.id, channel.id))
            await db.commit()
        await interaction.response.send_message(f"Welcome channel has been set to {channel.mention}")

    @nextcord.slash_command(name="set_welcome_message", description="Set the welcome message for the server.")
    @commands.has_permissions(manage_channels=True)
    async def set_welcome_message(self, interaction: nextcord.Interaction, *, message: str):
        await self.ensure_db()
        async with aiosqlite.connect("db/welcome.db") as db:
            await db.execute("UPDATE welcome SET welcome_msg = ? WHERE guild_id = ?", (message, interaction.guild.id))
            await db.commit()
        await interaction.response.send_message("Welcome message has been set.")

    @nextcord.slash_command(name="set_bye_message", description="Set the bye message for the server.")
    @commands.has_permissions(manage_channels=True)
    async def set_bye_message(self, interaction: nextcord.Interaction, *, message: str):
        await self.ensure_db()
        async with aiosqlite.connect("db/welcome.db") as db:
            await db.execute("UPDATE welcome SET bye_msg = ? WHERE guild_id = ?", (message, interaction.guild.id))
            await db.commit()
        await interaction.response.send_message("Bye message has been set.")

    @nextcord.slash_command(name="welcome_display", description="Display the current welcome settings for the server.")
    @commands.has_permissions(manage_channels=True)
    async def welcome_display(self, interaction: nextcord.Interaction):
        await self.ensure_db()
        result = await self.get_welcome_settings(interaction.guild.id)

        if result:
            channel_id, welcome_msg, bye_msg, is_enabled = result
            channel = interaction.guild.get_channel(channel_id)
            channel_mention = channel.mention if channel else "Not set"
            status = ":green_circle: Enabled" if is_enabled else ":red_circle: Disabled"

            embed = nextcord.Embed(
                title=f"Welcome System settings for {interaction.guild.name}",
                description=(
                    f"Status: **{status}**\n"
                    f"Welcome Channel: **{channel_mention}**\n"
                    f"Welcome Message: **{welcome_msg or 'Default welcome message'}**\n"
                    f"Bye Message: **{bye_msg or 'Default bye message'}**"
                )
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Welcome System is not configured in this server.", ephemeral=True)

    @nextcord.slash_command(name="enable_welcome", description="Enable the welcome and bye messages for the server.")
    @commands.has_permissions(manage_channels=True)
    async def enable_welcome(self, interaction: nextcord.Interaction):
        await self.ensure_db()
        async with aiosqlite.connect("db/welcome.db") as db:
            await db.execute("UPDATE welcome SET is_enabled = 1 WHERE guild_id = ?", (interaction.guild.id,))
            await db.commit()
        embed = nextcord.Embed(title="⛔ ┃ Welcome System Enable", description="Welcome and Bye messages are now enabled", color=0x00FF00)
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name="disable_welcome", description="Disable the welcome and bye messages for the server.")
    @commands.has_permissions(manage_channels=True)
    async def disable_welcome(self, interaction: nextcord.Interaction):
        await self.ensure_db()
        async with aiosqlite.connect("db/welcome.db") as db:
            await db.execute("UPDATE welcome SET is_enabled = 0 WHERE guild_id = ?", (interaction.guild.id,))
            await db.commit()
        embed = nextcord.Embed(title="⛔ ┃ Welcome System Disable", description="Welcome and Bye messages are now disabled", color=0xFF0000)
        await interaction.response.send_message(embed=embed)

