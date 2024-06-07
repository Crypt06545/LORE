import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
from dotenv import load_dotenv



#hide all confirm
class hideallConfirm(nextcord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout = timeout)

    @nextcord.ui.button(label = "Confirm", style = nextcord.ButtonStyle.green)
    async def hideall_confirm(self, button: nextcord.ui.Button ,interaction: nextcord.Interaction):
        if interaction.user != interaction.message.interaction.user:
            return await interaction.response.send_message("> This is not for you!", ephemeral=True)
        await interaction.response.defer()
        for channel in interaction.guild.channels:
            overwrite = channel.overwrites_for(interaction.guild.default_role)
            overwrite.read_messages = False
            await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        emb = nextcord.Embed(title=":closed_lock_with_key: ┃ All Channels Hid! ┃ :closed_lock_with_key:",
                             description=f"> {interaction.user.mention} had hid all channels in the server.")
        await interaction.followup.send(embed=emb)
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

    #cancel button
    @nextcord.ui.button(label = "Cancel", style = nextcord.ButtonStyle.red)
    async def hideall_cancel(self, button: nextcord.ui.Button,interaction: nextcord.Interaction):
        if interaction.user != interaction.message.interaction.user:
            return await interaction.response.send_message("> This is not for you!", ephemeral=True)
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message("> Process Canceled.")

#show all confirm
class showallConfirm(nextcord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout = timeout)

    @nextcord.ui.button(label = "Confirm", style = nextcord.ButtonStyle.green)
    async def showall_confirm(self, button: nextcord.ui.Button,interaction: nextcord.Interaction):
        # user = interaction.user
        if interaction.user != interaction.message.interaction.user:
            return await interaction.response.send_message("> This is not for you!", ephemeral=True)
        await interaction.response.defer()
        for channel in interaction.guild.channels:
            overwrite = channel.overwrites_for(interaction.guild.default_role)
            overwrite.read_messages = True
            await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        emb = nextcord.Embed(title="👁️ ┃ Channels Showed! ┃ 👁️",
                             description=f"> {interaction.user.mention} had unhid all channels in the server.")
        await interaction.followup.send(embed=emb)
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

    #cancel button
    @nextcord.ui.button(label = "Cancel", style = nextcord.ButtonStyle.red)
    async def showall_cancel(self,button: nextcord.ui.Button ,interaction: nextcord.Interaction):
        if interaction.user != interaction.message.interaction.user:
            return await interaction.response.send_message("> This is not for you!", ephemeral=True)
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message("> Process Canceled.")

# Hide Class
class Hide(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #wakin~
    @commands.Cog.listener()
    async def on_ready(self):
        print("Hide is online.")

    #hide
    @nextcord.slash_command(name="hide", description="Hide a channel.")
    async def hidechat(self, interaction: Interaction, 
                       channel: nextcord.TextChannel = SlashOption(description="Channel to hide (default is current channel).", required=False)):
        channel = channel or interaction.channel
        overwrite = channel.overwrites_for(interaction.guild.default_role)
        if overwrite.read_messages == False:
            await interaction.response.send_message("> The channel is already hidden!", ephemeral=True)
            return
        overwrite.read_messages = False
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        emb = nextcord.Embed(title=":closed_lock_with_key: ┃ Channel Hid!", description=f"> **{channel.mention}** has been hidden.", color=0x2F3136)
        await interaction.response.send_message(embed=emb)

    #hide all
    @nextcord.slash_command(name="hideall", description="Hide all channels in the server.")
    async def hideall(self, interaction: Interaction):
        hideall_em = nextcord.Embed(title="Confirm", description="Are you sure that you want to hide all your channels?")
        view = hideallConfirm()
        await interaction.response.send_message(embed=hideall_em, view=view)

    #show
    @nextcord.slash_command(name="show", description="Show a hidden channel.")
    async def showchat(self, interaction: Interaction, 
                       channel: nextcord.TextChannel = SlashOption(description="Channel to unhide (default is current channel).", required=False)):
        channel = channel or interaction.channel
        overwrite = channel.overwrites_for(interaction.guild.default_role)
        if overwrite.read_messages == True:
            return await interaction.response.send_message("> The channel is already shown!", ephemeral=True)
        overwrite.read_messages = True
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        emb = nextcord.Embed(title="👁️ ┃ Channel Showed!", description=f"> **{channel.mention}** has been shown.", color=0x2F3136)
        await interaction.response.send_message(embed=emb)

    #show all
    @nextcord.slash_command(name="showall", description="Unhide all channels in the server.")
    async def showall(self, interaction: Interaction):
        hideall_em = nextcord.Embed(title="Confirm", description="Are you sure that you want to unhide all your channels?")
        view = showallConfirm()
        await interaction.response.send_message(embed=hideall_em, view=view)
