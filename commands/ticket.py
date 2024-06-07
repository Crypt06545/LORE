import nextcord
from nextcord.ext import commands
from nextcord import ui, utils, Interaction, SlashOption
import os
from datetime import datetime
import aiosqlite
import time
import asyncio


async def add_user_to_channel(channel_id, user_id):
    async with aiosqlite.connect("db/tickets_user.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (user INTEGER, channel INTEGER)")  # Create table if not exists
        await db.commit()  # Save changes

        await db.execute("INSERT INTO users (user, channel) VALUES (?, ?)", (user_id, channel_id))
        await db.commit()  # Save changes

async def remove_user_permissions(channel, user_id):
    user = channel.guild.get_member(user_id)
    if user:
        await channel.set_permissions(user, overwrite=None)

class TicketModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Send Your Feedback")
        self.add_item(ui.TextInput(label="What is your issue?", style=nextcord.TextInputStyle.short, placeholder="Describe your issue.", required=True, max_length=1000))

    async def callback(self, interaction: Interaction):
        issue = self.children[0].value
        embed = nextcord.Embed(title="Issue", description=issue, timestamp=datetime.now())
        embed.set_author(name=str(interaction.user), icon_url=interaction.user.avatar.url)
        await ticket_channel.send(ticket_sentence, embed=embed, view=MainView())
        await interaction.response.send_message(f"I've opened a ticket for you at {ticket_channel.mention}!", ephemeral=True)

class TicketLauncher(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 600, commands.BucketType.member)

    @ui.button(label="Create a Ticket", style=nextcord.ButtonStyle.blurple, custom_id="ticket_button", emoji="📩")
    async def ticket(self, button: ui.Button, interaction: Interaction):
        ticket = utils.get(interaction.guild.text_channels, name=f"ticket-for-{interaction.user.name.replace(' ', '-')}")
        if ticket:
            await interaction.response.send_message(f"You already have a ticket open at {ticket.mention}!", ephemeral=True)
        else:
            overwrites = {
                interaction.guild.default_role: nextcord.PermissionOverwrite(view_channel=False),
                interaction.user: nextcord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True, attach_files=True, embed_links=True),
                interaction.guild.me: nextcord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            }
            async with aiosqlite.connect("db/tickets_role.db") as db:
                async with db.cursor() as cursor:
                    await cursor.execute("CREATE TABLE IF NOT EXISTS roles (role INTEGER, guild INTEGER)") # Create the table if not exists
                    await cursor.execute("SELECT role FROM roles WHERE guild = ?", (interaction.guild.id,))
                    data = await cursor.fetchone()
                    if data: ticket_role = data[0]
                    else: ticket_role = None
            global ticket_channel, ticket_sentence
            if ticket_role:
                ticket_role = interaction.guild.get_role(ticket_role)
                overwrites[ticket_role] = nextcord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True, attach_files=True, embed_links=True)
                ticket_sentence = f"{ticket_role.mention}, {interaction.user.mention} created a ticket!"
            else:
                ticket_sentence = f"{interaction.user.mention} created a ticket!"
            guild = interaction.guild
            category = utils.get(guild.categories, name="tickets")
            if category is None:
                category = await guild.create_category("tickets")
            try:
                ticket_channel = await interaction.guild.create_text_channel(name=f"ticket-for-{interaction.user.name}", overwrites=overwrites, reason=f"Ticket for {interaction.user.name}", category=category)
                await add_user_to_channel(ticket_channel.id, interaction.user.id)
            except:
                return await interaction.response.send_message("Ticket creation failed! Make sure I have `Manage Channels` permissions!", ephemeral=True)
            await interaction.response.send_modal(TicketModal())

class ArchiveConfirm(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Confirm", style=nextcord.ButtonStyle.red, custom_id="confirm")
    async def archive_confirm_button(self, button: ui.Button, interaction: Interaction):
        if interaction.channel.name.startswith("archive-") and interaction.channel.category.name.startswith("ticketarchive"):
            return await interaction.response.send_message("This ticket is already archived!", ephemeral=True)
        await interaction.response.send_message("This ticket will be archived in 5 seconds", ephemeral=True)
        time.sleep(3)
        channel = interaction.channel

        async with aiosqlite.connect("db/tickets_user.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT user FROM users WHERE channel = ?", (channel.id,))
                data = await cursor.fetchone()
        await remove_user_permissions(interaction.channel, data[0])

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        guild = interaction.guild
        category2 = utils.get(guild.categories, name="ticketarchive")
        if category2 is None:
            category2 = await guild.create_category("ticketarchive")
        try:
            new_channel_name = f"archive-{interaction.channel.name}-{timestamp}"
            await interaction.channel.edit(category=category2, name=new_channel_name)
        except:
            await interaction.response.send_message("Channel rename failed! Make sure I have `Manage Channels` permissions!", ephemeral=True)

class CloseConfirm(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Confirm", style=nextcord.ButtonStyle.red, custom_id="confirm")
    async def close_confirm_button(self, button: ui.Button, interaction: Interaction):
        try:
            await interaction.channel.delete()
        except:
            await interaction.response.send_message("Channel deletion failed! Make sure I have `Manage Channels` permissions!", ephemeral=True)


class MainView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Archive Ticket", style=nextcord.ButtonStyle.blurple, custom_id="archive")
    async def archive(self, button: ui.Button, interaction: Interaction):
        embed = nextcord.Embed(title="Are you sure you want to archive this ticket?", color=nextcord.Colour.blurple())
        await interaction.response.send_message(embed=embed, view=ArchiveConfirm(), ephemeral=True)

    @ui.button(label="Close Ticket", style=nextcord.ButtonStyle.red, custom_id="close")
    async def close(self, button: ui.Button, interaction: Interaction):
        embed = nextcord.Embed(title="Are you sure you want to close this ticket?", color=nextcord.Colour.blurple())
        await interaction.response.send_message(embed=embed, view=CloseConfirm(), ephemeral=True)

    @ui.button(label="Transcript", style=nextcord.ButtonStyle.blurple, custom_id="transcript")
    async def transcript(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        transcript_filename = f"{interaction.channel.id}.md"
        if os.path.exists(transcript_filename):
            return await interaction.followup.send(f"A transcript is already being generated!", ephemeral=True)
        
        # Create the transcript
        with open(transcript_filename, 'w', encoding='utf-8') as f:
            f.write(f"# Transcript of {interaction.channel.name}:\n\n")
            async for message in interaction.channel.history(limit=None, oldest_first=True):
                created = datetime.strftime(message.created_at, "%m/%d/%Y at %H:%M:%S")
                if message.edited_at:
                    edited = datetime.strftime(message.edited_at, "%m/%d/%Y at %H:%M:%S")
                    f.write(f"{message.author} on {created}: {message.clean_content} (Edited at {edited})\n")
                else:
                    f.write(f"{message.author} on {created}: {message.clean_content}\n")
            generated = datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
            f.write(f"\n*Generated at {generated} by {selfbot}*\n*Date Formatting: MM/DD/YY*\n*Time Zone: UTC*")
        
        # Ensure the file is closed before opening it again for reading
        with open(transcript_filename, 'rb') as f:
            await interaction.followup.send(file=nextcord.File(f, f"{interaction.channel.name}.md"))
        
        # Add a slight delay before deleting the file to ensure it is no longer in use
        await asyncio.sleep(1)
        
        # Delete the file after sending it
        try:
            os.remove(transcript_filename)
        except PermissionError as e:
            await interaction.followup.send(f"Failed to delete transcript file: {e}", ephemeral=True)




class Ticket(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        global selfbot
        selfbot = self.bot.user
        print("Ticket is online.")

    async def open_ticket_context_menu(self, interaction: Interaction, member: nextcord.Member):
        if interaction.user.top_role <= member.top_role and not interaction.user == interaction.guild.owner:
            return await interaction.response.send_message(f"Your role must be higher than {member.mention}'s role to open a ticket for them!", ephemeral=True)
        ticket = utils.get(interaction.guild.text_channels, name=f"ticket-for-{member.name.replace(' ', '-')}")
        if ticket:
            await interaction.response.send_message(f"{member.name} already has a ticket open at {ticket.mention}!", ephemeral=True)
        else:
            overwrites = {
                interaction.guild.default_role: nextcord.PermissionOverwrite(view_channel=False),
                member: nextcord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True, attach_files=True, embed_links=True),
                interaction.guild.me: nextcord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            }
            async with aiosqlite.connect("db/tickets_role.db") as db:
                async with db.cursor() as cursor:
                    await cursor.execute("CREATE TABLE IF NOT EXISTS roles (role INTEGER, guild INTEGER)") # Create the table if not exists
                    await cursor.execute("SELECT role FROM roles WHERE guild = ?", (interaction.guild.id,))
                    data = await cursor.fetchone()
                    if data: ticket_role = data[0]
                    else: ticket_role = None
            if ticket_role:
                ticket_role = interaction.guild.get_role(ticket_role)
                overwrites[ticket_role] = nextcord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True, attach_files=True, embed_links=True)
                ticket_sentence = f"{ticket_role.mention}, {member.mention} created a ticket!"
            else:
                ticket_sentence = f"{member.mention} created a ticket!"
            guild = interaction.guild
            category = utils.get(guild.categories, name="tickets")
            if category is None:
                category = await guild.create_category("tickets")
            try:
                ticket_channel = await interaction.guild.create_text_channel(name=f"ticket-for-{member.name}", overwrites=overwrites, reason=f"Ticket for {member.name}", category=category)
                await add_user_to_channel(ticket_channel.id, member.id)
            except:
                return await interaction.response.send_message("Ticket creation failed! Make sure I have `Manage Channels` permissions!", ephemeral=True)
            await ticket_channel.send(ticket_sentence, view=MainView())
            await interaction.response.send_message(f"I've opened a ticket for you at {ticket_channel.mention}!", ephemeral=True)

    @nextcord.slash_command(description="Set the support role for tickets.")
    @commands.has_permissions(administrator=True)
    async def ticketrole(self, interaction: Interaction, role: nextcord.Role = SlashOption(name="role", description="The role to set as the support role.", required=True)):
        async with aiosqlite.connect("db/tickets_role.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS roles (role INTEGER, guild INTEGER)")
            await db.execute("INSERT INTO roles (role, guild) VALUES (?, ?)", (role.id, interaction.guild.id))
            await db.commit()
        await interaction.response.send_message(f"Successfully set {role.mention} as the support role!")

    @nextcord.slash_command(description="Send a ticket launcher.")
    @commands.has_permissions(administrator=True)
    async def ticketlauncher(self, interaction: Interaction):
        await interaction.response.send_message("Click the button to create a ticket.", view=TicketLauncher())

