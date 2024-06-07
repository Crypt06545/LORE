import ast
import aiosqlite
import nextcord
from nextcord import SlashOption
from nextcord.ext import commands
import re
from datetime import timedelta
from datetime import datetime


# Filter Class
class Censor(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Waking
    @commands.Cog.listener()
    async def on_ready(self):
        print("Censor is online.")

    # Censor enable
    @nextcord.slash_command(name="censor_enable", description="Enable the Censor System")
    async def censor_enable(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You don't have permission to manage channels.", ephemeral=True)
            return
        
        async with aiosqlite.connect("db/censor.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS censor (guild INTEGER, switch INTEGER, words TEXT, punishment TEXT, whitelist INTEGER, alert INTEGER, censor_links TEXT, censor_invites TEXT)")
                await cursor.execute("SELECT switch FROM censor WHERE guild = ?", (interaction.guild.id,))
                data = await cursor.fetchone()
                if data:
                    await interaction.response.send_message("Your censor system is already enabled.", ephemeral=True)
                else:
                    await cursor.execute("INSERT INTO censor (guild, switch, words, punishment, whitelist, alert, censor_links, censor_invites) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (interaction.guild.id, 1, "[]", "none", 0, 0, "disabled", "disabled",))
                    embed = nextcord.Embed(title="⛔ ┃ Censor System Enable", description="Censor System is now enabled", color=0x000000)
                    await interaction.response.send_message(embed=embed)
            await db.commit()

    # Censor disable
    @nextcord.slash_command(name="censor_disable", description="Disable the Censor System")
    async def censor_disable(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You don't have permission to manage channels.", ephemeral=True)
            return
        
        async with aiosqlite.connect("db/censor.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS censor (guild INTEGER, switch INTEGER, words TEXT, punishment TEXT, whitelist INTEGER, alert INTEGER, censor_links TEXT, censor_invites TEXT)")
                await cursor.execute("SELECT switch FROM censor WHERE guild = ?", (interaction.guild.id,))
                data = await cursor.fetchone()
                if data:
                    await cursor.execute("DELETE FROM censor WHERE guild = ?", (interaction.guild.id,))
                    embed = nextcord.Embed(title="⛔ ┃ Censor System Disable", description="Censor System is now disabled", color=0x000000)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("Censor System is already disabled.", ephemeral=True)
            await db.commit()

    # Censor words
    @nextcord.slash_command(name="censor_words", description="Add or remove words from the Censor System")
    async def censor_words(self, interaction: nextcord.Interaction, option: str = SlashOption(description="Select option", choices={"add": "add", "remove": "remove"}), words: str = SlashOption(description="Use a comma ',' to separate each word")):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You don't have permission to manage channels.", ephemeral=True)
            return
        
        async with aiosqlite.connect("db/censor.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS censor (guild INTEGER, switch INTEGER, words TEXT, punishment TEXT, whitelist INTEGER, alert INTEGER, censor_links TEXT, censor_invites TEXT)")
                await cursor.execute("SELECT * FROM censor WHERE guild = ?", (interaction.guild.id,))
                data = await cursor.fetchone()
                if data:  # If system is enabled
                    existing_words = ast.literal_eval(data[2])
                    if option == "add":  # If user is adding words
                        already_added_words = []
                        new_words = []
                        added_words = words.split(",")
                        for word in added_words:
                            word = word.strip()
                            if word in existing_words:  # If word is already added
                                already_added_words.append(word)
                            else:  # If word is not added yet
                                new_words.append(word)
                                existing_words.append(word)
                        # Add data to db and send to user
                        await cursor.execute("UPDATE censor SET words = ? WHERE guild = ?", (str(existing_words), interaction.guild.id,))
                        embed = nextcord.Embed(title="⛔ ┃ Censor System Words", description=f"`{', '.join(new_words)}` had been added to the system", color=0x000000)
                        if already_added_words:
                            embed.set_footer(text=f"Note: {', '.join(already_added_words)} had already been added before. Check /censor display to view all the settings")
                        await interaction.response.send_message(embed=embed)
                    if option == "remove":  # If user is removing words
                        already_removed_words = []
                        to_remove_words = []
                        removed_words = words.split(",")
                        for word in removed_words:
                            word = word.strip()
                            if word in existing_words:  # If word is really added
                                to_remove_words.append(word)
                                existing_words.remove(word)
                            else:  # If word is not added
                                already_removed_words.append(word)
                        # Add data to db and send to user
                        await cursor.execute("UPDATE censor SET words = ? WHERE guild = ?", (str(existing_words), interaction.guild.id,))
                        embed = nextcord.Embed(title="⛔ ┃ Censor System Words", description=f"`{', '.join(to_remove_words)}` had been removed from the system", color=0x000000)
                        if already_removed_words:
                            embed.set_footer(text=f"Note: {', '.join(already_removed_words)} are not on the system. Check /censor display to view all the settings")
                        await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("Censor System is not enabled in this server.\nEnable it from /censor enable", ephemeral=True)
            await db.commit()

    # Censor punishment
    @nextcord.slash_command(name="censor_punishment", description="Sets a punishment for the Censor System")
    async def censor_punishment(self, interaction: nextcord.Interaction, punishment: str = SlashOption(description="The punishment.", choices={"none": "none", "mute": "mute", "timeout": "timeout", "warn": "warn", "kick": "kick", "ban": "ban"})):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You don't have permission to manage channels.", ephemeral=True)
            return
        
        async with aiosqlite.connect("db/censor.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS censor (guild INTEGER, switch INTEGER, words TEXT, punishment TEXT, whitelist INTEGER, alert INTEGER, censor_links TEXT, censor_invites TEXT)")
                await cursor.execute("SELECT switch FROM censor WHERE guild = ?", (interaction.guild.id,))
                data = await cursor.fetchone()
                if data:
                    await cursor.execute("UPDATE censor SET punishment = ? WHERE guild = ?", (punishment, interaction.guild.id,))
                    embed = nextcord.Embed(title="⛔ ┃ Censor System Punishment", description=f"Censor System punishment has been updated to `{punishment}`", color=0x000000)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("Censor System is not enabled in this server.\nEnable it from /censor enable", ephemeral=True)
            await db.commit()

    # Censor whitelist
    @nextcord.slash_command(name="censor_whitelist", description="Whitelist channels from the Censor System")
    async def censor_whitelist(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You don't have permission to manage channels.", ephemeral=True)
            return
        
        async with aiosqlite.connect("db/censor.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS censor (guild INTEGER, switch INTEGER, words TEXT, punishment TEXT, whitelist INTEGER, alert INTEGER, censor_links TEXT, censor_invites TEXT)")
                await cursor.execute("SELECT switch FROM censor WHERE guild = ?", (interaction.guild.id,))
                data = await cursor.fetchone()
                if data:
                    await cursor.execute("UPDATE censor SET whitelist = ? WHERE guild = ?", (channel.id, interaction.guild.id,))
                    embed = nextcord.Embed(title="⛔ ┃ Censor System Whitelist", description=f"`{channel.mention}` has been whitelisted from the Censor System", color=0x000000)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("Censor System is not enabled in this server.\nEnable it from /censor enable", ephemeral=True)
            await db.commit()


    # Censor alert channel
    @nextcord.slash_command(name="censor_alert", description="Set an alert channel for the Censor System")
    @commands.has_permissions(manage_channels=True)
    async def censor_alert(self, interaction: nextcord.Interaction, 
                           channel: nextcord.TextChannel = SlashOption(description="The channel to send alerts to")):
        async with aiosqlite.connect("db/censor.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS censor (guild INTEGER, switch INTEGER, words TEXT, punishment TEXT, whitelist INTEGER, alert INTEGER, censor_links TEXT, censor_invites TEXT)")
                await cursor.execute("SELECT * FROM censor WHERE guild = ?", (interaction.guild.id,))
                data = await cursor.fetchone()
                if data:
                    await cursor.execute("UPDATE censor SET alert = ? WHERE guild = ?", (str(channel.id), interaction.guild.id,))
                else:
                    return await interaction.response.send_message("Censor System is not enabled in this server.\nEnable it from </censor enable:1208140083711185017>", ephemeral=True)
                embed = nextcord.Embed(title="⛔ ┃ Censor System Alert", description=f"{channel.mention} is now the alert channel", color=0x000000)
                await interaction.response.send_message(embed=embed)
            await db.commit()

    # Censor links
    @nextcord.slash_command(name="censor_links", description="Enable/Disable censoring all links")
    @commands.has_permissions(manage_channels=True)
    async def censor_links(self, interaction:  nextcord.Interaction):
        async with aiosqlite.connect("db/censor.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS censor (guild INTEGER, switch INTEGER, words TEXT, punishment TEXT, whitelist INTEGER, alert INTEGER, censor_links TEXT, censor_invites TEXT)")
                await cursor.execute("SELECT * FROM censor WHERE guild = ?", (interaction.guild.id,))
                data = await cursor.fetchone()
                if data:
                    if data[6] == "enabled":
                        await cursor.execute("UPDATE censor SET censor_links = ? WHERE guild = ?", ("disabled", interaction.guild.id,))
                        embed = nextcord.Embed(title="⛔ ┃ Censoring Links Disabled", description="Censoring all links is now disabled", color=0x000000)
                        await interaction.response.send_message(embed=embed)
                    elif data[6] == "disabled":
                        await cursor.execute("UPDATE censor SET censor_links = ? WHERE guild = ?", ("enabled", interaction.guild.id,))
                        embed = nextcord.Embed(title="⛔ ┃ Censoring Links Enabled", description="Censoring all links is now enabled", color=0x000000)
                        await interaction.response.send_message(embed=embed)
                else:
                    return await interaction.response.send_message("Censor System is not enabled in this server.\nEnable it from </censor enable:1208140083711185017>", ephemeral=True)
            await db.commit()

    # Censor invites
    @nextcord.slash_command(name="censor_invites", description="Enable/Disable censoring all invites")
    @commands.has_permissions(manage_channels=True)
    async def censor_invites(self, interaction:  nextcord.Interaction):
        async with aiosqlite.connect("db/censor.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS censor (guild INTEGER, switch INTEGER, words TEXT, punishment TEXT, whitelist INTEGER, alert INTEGER, censor_links TEXT, censor_invites TEXT)")
                await cursor.execute("SELECT * FROM censor WHERE guild = ?", (interaction.guild.id,))
                data = await cursor.fetchone()
                if data:
                    if data[7] == "enabled":
                        await cursor.execute("UPDATE censor SET censor_invites = ? WHERE guild = ?", ("disabled", interaction.guild.id,))
                        embed = nextcord.Embed(title="⛔ ┃ Censoring Invites Disabled", description="Censoring other server's invites is now disabled", color=0x000000)
                        await interaction.response.send_message(embed=embed)
                    elif data[7] == "disabled":
                        await cursor.execute("UPDATE censor SET censor_invites = ? WHERE guild = ?", ("enabled", interaction.guild.id,))
                        embed = nextcord.Embed(title="⛔ ┃ Censoring Invites Enabled", description="Censoring other server's invites is now enabled", color=0x000000)
                        await interaction.response.send_message(embed=embed)
                else:
                    return await interaction.response.send_message("Censor System is not enabled in this server.\nEnable it from </censor enable:1208140083711185017>", ephemeral=True)
            await db.commit()

    # Censor display
    @nextcord.slash_command(name="censor_display", description="Display Censor System settings in this server")
    @commands.has_permissions(manage_channels=True)
    async def censor_display(self, interaction:  nextcord.Interaction):
        async with aiosqlite.connect("db/censor.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS censor (guild INTEGER, switch INTEGER, words TEXT, punishment TEXT, whitelist INTEGER, alert INTEGER, censor_links TEXT, censor_invites TEXT)")
                await cursor.execute("SELECT * FROM censor WHERE guild = ?", (interaction.guild.id,))
                data = await cursor.fetchone()
                if data:
                    status = ":green_circle: Enabled" if data[1] == 1 else ":red_circle: Disabled"
                    words = "None" if data[2] == "[]" else ", ".join(ast.literal_eval(data[2]))
                    punishment = str(data[3]).title()
                    whitelisted_channel = self.bot.get_channel(int(data[4]))
                    whitelisted_channel = whitelisted_channel.mention if whitelisted_channel else "None"
                    alert_channel = self.bot.get_channel(int(data[5]))
                    alert_channel = alert_channel.mention if alert_channel else "None"
                    censor_links = str(data[6]).title()
                    censor_invites = str(data[7]).title()
                    embed = nextcord.Embed(title=f"Censor System settings for {interaction.guild.name}",
                                           description=f"Status: **{status}**\nCensored Words: **{words}**\nPunishment: **{punishment}**\nAlert Channel: **{alert_channel}**\nWhitelisted Channel: **{whitelisted_channel}**\nCensor Links: **{censor_links}**\nCensor Invites: **{censor_invites}**")
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("Censor System is not enabled in this server.\nEnable it from </censor enable:1208140083711185017>", ephemeral=True)

    # On message events
    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return  # If bot ignore it

        # Open Censor database
        async with aiosqlite.connect("db/censor.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS censor (guild INTEGER, switch INTEGER, words TEXT, punishment TEXT, whitelist INTEGER, alert INTEGER, censor_links TEXT, censor_invites TEXT)")
                await cursor.execute("SELECT * FROM censor WHERE guild = ?", (message.guild.id,))
                data = await cursor.fetchone()

        # If censor is enabled
        if data:
            message_content = message.content
            message_censored = False
            censored_content = ""
            censored_words = ast.literal_eval(data[2])
            punishment = data[3]
            whitelisted_channel_id = int(data[4])
            alert_channel_id = int(data[5])
            censor_links = data[6]
            censor_invites = data[7]

            # If channel is not whitelisted
            if message.channel.id != whitelisted_channel_id:
                # If censor invites is enabled
                if censor_invites == "enabled":
                    if "discord.gg/" in message_content:
                        message_censored = True
                        censored_content = "Server invite"

                # If censor links is enabled and message not deleted
                if not message_censored and censor_links == "enabled":
                    pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
                    is_link = bool(re.search(pattern, message_content))
                    if is_link:
                        message_censored = True
                        censored_content = "Link"

                # If there are censor words and message not deleted
                if not message_censored and censored_words:
                    for word in censored_words:
                        if word in message_content:
                            message_censored = True
                            censored_content = word

                # If message should be censored
                if message_censored:
                    try:
                        await message.delete()
                    except:  # If bot doesn't have permissions to delete the message
                        if alert_channel_id != 0:
                            alert_channel = self.bot.get_channel(alert_channel_id)
                            embed = nextcord.Embed(description=f"**⛔ I can't censor a message sent by {message.author.mention} in {message.channel.mention} that contains `{censored_content}`. Check my permissions. [Jump to Message]({message.jump_url})**", color=0x000000, timestamp=datetime.now())
                            embed.set_author(name=message.author, icon_url=message.author.avatar.url)
                            embed.add_field(name="Message:", value=f"```{message_content}```")
                            embed.set_footer(text=message.guild.name)
                            return await alert_channel.send(embed=embed)

                    # If there should be a punishment
                    if punishment != "none":
                        if punishment != "none":
                            if message.guild.me.top_role <= message.author.top_role:
                                if alert_channel_id != 0:  # If bot's role is lower than the member
                                    alert_channel = self.bot.get_channel(alert_channel_id)
                                    embed = nextcord.Embed(description=f"**⛔ I can't punish {message.author.mention} for sending a message in {message.channel.mention} that contains `{censored_content}`. Check my roles. [Jump to Message]({message.jump_url})**", color=0x000000, timestamp=datetime.now())
                                    embed.set_author(name=message.author, icon_url=message.author.avatar.url)
                                    embed.add_field(name="Message:", value=f"```{message_content}```")
                                    embed.set_footer(text=message.guild.name)
                                    return await alert_channel.send(embed=embed)

                            if punishment == "mute":
                                mutedRole = nextcord.utils.get(message.guild.roles, name="SB-Muted")
                                if not mutedRole:
                                    mutedRole = await message.guild.create_role(name="SB-Muted")
                                    for channel in message.guild.channels:
                                        await channel.set_permissions(mutedRole, send_messages=False)
                                await message.author.add_roles(mutedRole)
                                await message.author.send(f"You have been muted in {message.guild.name} for sending a censored message\n`{censored_content}`")
                            elif punishment == "timeout":
                                await message.author.timeout(timedelta(minutes=10), reason="Sending a message that contains censored content")
                                auther_message = f"You have been timed out in {message.guild.name} for sending a censored message\n`{censored_content}`"
                            elif punishment == "warn":
                                async with aiosqlite.connect("db/warnings.db") as db:
                                    async with db.cursor() as cursor:
                                        await cursor.execute("CREATE TABLE IF NOT EXISTS warnings (warns INTEGER, member INTEGER, guild INTEGER)")
                                        await cursor.execute("SELECT warns FROM warnings WHERE member = ? AND guild = ?", (message.author.id, message.guild.id,))
                                        data = await cursor.fetchone()
                                        if data:
                                            await cursor.execute("UPDATE warnings SET warns = ? WHERE member = ? AND guild = ?", (data[0] + 1, message.author.id, message.guild.id,))
                                        else:
                                            await cursor.execute("INSERT INTO warnings (warns, member, guild) VALUES (?, ?, ?)", (1, message.author.id, message.guild.id,))
                                    await db.commit()
                                auther_message = f"You have been warned in {message.guild.name} for sending a censored message\n`{censored_content}`"
                            elif punishment == "kick":
                                await message.author.kick(reason="Sending a message that contains censored content")
                                auther_message = f"You have been kicked out from {message.guild.name} for sending a censored message\n`{censored_content}`"
                            elif punishment == "ban":
                                await message.author.ban(reason="Sending a message that contains censored content")
                                auther_message = f"You have been banned from {message.guild.name} for sending a censored message\n`{censored_content}`"

                    # If everything is fine and there is an alert channel
                    if alert_channel_id != 0:
                        alert_channel = self.bot.get_channel(alert_channel_id)
                        embed = nextcord.Embed(description=f"**⛔ I censored a message sent by {message.author.mention} in {message.channel.mention} because it contained `{censored_content}`**", color=0x000000, timestamp=datetime.now())
                        embed.set_author(name=message.author, icon_url=message.author.avatar.url)
                        embed.add_field(name="Punishment:", value=f"```{punishment}```")
                        embed.add_field(name="Message:", value=f"```{message_content}```")
                        embed.set_footer(text=message.guild.name)
                        await alert_channel.send(embed=embed)
                        await message.author.send(auther_message)




# # Add Cog to bot
# async def setup(bot: commands.Bot):
#     await bot.add_cog(Censor(bot))
