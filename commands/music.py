import nextcord
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands
from wavelink.ext import spotify
import wavelink
import datetime
from dotenv import load_dotenv

import asyncio


class WavelinkPlayer(wavelink.Player, nextcord.VoiceProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = False
        self.ctx = None  # Initialize the ctx attribute
        self.interaction = None  # Initialize the interaction attribute

class ControlPanel(nextcord.ui.View):
    def __init__(self, vc, user, msg):
        super().__init__()
        self.vc = vc
        self.user = user  # Save the user who initiated the command
        self.msg = msg    # Save the message to update
    
    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message("You can't use this control panel. Run the command yourself to use these buttons.", ephemeral=True)
            return False
        return True
    
    @nextcord.ui.button(label="Resume", style=nextcord.ButtonStyle.green, emoji="▶️")
    async def resume(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.vc.resume()
        # await interaction.response.send_message("Resumed the music.", ephemeral=True)
    
    @nextcord.ui.button(label="Pause", style=nextcord.ButtonStyle.red, emoji="⏸️")
    async def pause(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.vc.pause()
        # await interaction.response.send_message("Paused the music.", ephemeral=True)
    
    @nextcord.ui.button(label="Stop", style=nextcord.ButtonStyle.red, emoji="⏹️")
    async def stop(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.vc.stop()
        # await interaction.response.send_message("Stopped the music.", ephemeral=True)

    @nextcord.ui.button(label="Volume Up", style=nextcord.ButtonStyle.blurple, emoji="🔊")
    async def volume_up(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        new_volume = min(self.vc.volume + 10, 100)
        await self.vc.set_volume(new_volume)
        # await interaction.response.send_message(f"Volume set to {new_volume}%.", ephemeral=True)
        await self.update_ui(interaction.message)

    @nextcord.ui.button(label="Volume Down", style=nextcord.ButtonStyle.blurple, emoji="🔉")
    async def volume_down(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        new_volume = max(self.vc.volume - 10, 0)
        await self.vc.set_volume(new_volume)
        # await interaction.response.send_message(f"Volume set to {new_volume}%.", ephemeral=True)
        await self.update_ui(interaction.message)
    
    @nextcord.ui.button(label="Queue", style=nextcord.ButtonStyle.gray, emoji="📜")
    async def queue(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.update_ui(interaction.message)

    @nextcord.ui.button(label="Skip", style=nextcord.ButtonStyle.blurple, emoji="⏭️")
    async def skip(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.vc.queue.is_empty:
            await interaction.response.send_message("The queue is empty.", ephemeral=True)
        else:
            next_song = self.vc.queue.get()
            await self.vc.play(next_song)
            # await interaction.response.send_message(f"Skipped to `{next_song.title}`", ephemeral=True)
            await self.update_ui(interaction.message)

    @nextcord.ui.button(label="Disconnect", style=nextcord.ButtonStyle.red, emoji="🔌")
    async def disconnect(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.vc.disconnect()
        # await interaction.response.send_message("Disconnected from the voice channel.", ephemeral=True)

    async def update_ui(self, message):
        if self.vc.queue.is_empty:
            queue_text = "The queue is empty."
        else:
            queue_text = "\n".join([f"{i+1}. {track.title}" for i, track in enumerate(self.vc.queue)])
        
        current_track = self.vc.source  # Use source instead of current
        em = nextcord.Embed(title="Music Panel", description=f"Now playing: {current_track.title if current_track else 'Nothing'}")
        em.add_field(name="Queue", value=queue_text, inline=False)
        await message.edit(embed=em, view=self)


class Music(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.loop.create_task(self.node_connect())

    async def node_connect(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, host='lavalink.ddns.net', port=7106, password='discord.gg/FqEQtEtUc9', https=False)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f'Node <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: WavelinkPlayer, track: wavelink.YouTubeTrack, reason):
        vc = player

        if vc.loop:
            return await vc.play(track)

        if vc.queue.is_empty:
            await asyncio.sleep(10)  # Wait for 10 seconds before disconnecting
            if vc.queue.is_empty and not vc.is_playing():
                await vc.disconnect()
        else:
            next_song = vc.queue.get()
            await vc.play(next_song)
            if vc.ctx:
                await vc.ctx.send(f"Now playing: {next_song.title}")
            elif vc.interaction:
                await vc.interaction.followup.send(f"Now playing: {next_song.title}")

    @commands.command()
    async def play(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack):
        if not ctx.voice_client:
            vc: WavelinkPlayer = await ctx.author.voice.channel.connect(cls=WavelinkPlayer)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Join a voice channel first.")
        else:
            vc: WavelinkPlayer = ctx.voice_client
            
        if vc.queue.is_empty and not vc.is_playing():
            await vc.play(search)
            await ctx.send(f'Playing `{search.title}`')
        else:
            await vc.queue.put_wait(search)
            await ctx.send(f'Added `{search.title}` to the queue...')
        vc.ctx = ctx
        try:
            if vc.loop: return
        except Exception:
            setattr(vc, "loop", False)
        
        # Show control panel
        em = nextcord.Embed(title="Music Panel", description="Control the bot using the buttons below.")
        view = ControlPanel(vc, ctx.author, await ctx.send(embed=em))  # Pass the author of the command
        await view.update_ui(view.msg)
        
    @nextcord.slash_command(description="Play a song")
    async def play(self, interaction: Interaction, channel: GuildChannel = SlashOption(channel_types=[ChannelType.voice], description="Voice Channel to Join"), search: str = SlashOption(description="Song Name")):
        await interaction.response.defer()
        search = await wavelink.YouTubeTrack.search(query=search, return_first=True)
        if not interaction.guild.voice_client:
            vc: WavelinkPlayer = await channel.connect(cls=WavelinkPlayer)
        elif not getattr(interaction.user.voice, "channel", None):
            return await interaction.followup.send("Join a voice channel first.")
        else:
            vc: WavelinkPlayer = interaction.guild.voice_client
        
        if vc.queue.is_empty and not vc.is_playing():
            await vc.play(search)
            await interaction.followup.send(f'Playing `{search.title}`')
        else:
            await vc.queue.put_wait(search)
            await interaction.followup.send(f'Added `{search.title}` to the queue...')
        vc.interaction = interaction
        try:
            if vc.loop: return
        except Exception:
            setattr(vc, "loop", False)
        
        # Show control panel
        em = nextcord.Embed(title="Music Panel", description="Control the bot using the buttons below.")
        view = ControlPanel(vc, interaction.user, await interaction.followup.send(embed=em))  # Pass the user of the interaction
        await view.update_ui(view.msg)

    @commands.command()
    async def pause(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Join a voice channel first.")
        else:
            vc: WavelinkPlayer = ctx.voice_client
        
        if not vc.is_playing():
            return await ctx.send("No music is playing.")
        
        await vc.pause()
        await ctx.send("Paused the music.")
        
    @commands.command()
    async def resume(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Join a voice channel first.")
        else:
            vc: WavelinkPlayer = ctx.voice_client
        if vc.is_playing():
            return await ctx.send("Music is already playing.")

        await vc.resume()
        await ctx.send("Resumed the music.")
        
    @commands.command()
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Join a voice channel first.")
        else:
            vc: WavelinkPlayer = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send("No music is playing.")
        
        try:
            next_song = vc.queue.get()
            await vc.play(next_song)
            await ctx.send(f"Now Playing `{next_song.title}`")
        except Exception:
            return await ctx.send("The queue is empty!")
        
        await vc.stop()
        await ctx.send("Stopped the song.")
        
    @commands.command()
    async def disconnect(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Join a voice channel first.")
        else:
            vc: WavelinkPlayer = ctx.voice_client
        
        await vc.disconnect()
        await ctx.send("Disconnected from the voice channel.")
        
    @commands.command()
    async def loop(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Join a voice channel first.")
        vc: WavelinkPlayer = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send("No music is playing.")
        try: 
            vc.loop ^= True
        except:
            setattr(vc, "loop", False)
        if vc.loop:
            return await ctx.send("Loop enabled.")
        else:
            return await ctx.send("Loop disabled.")

    @commands.command()
    async def queue(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Join a voice channel first.")
        vc: WavelinkPlayer = ctx.voice_client

        if vc.queue.is_empty:
            return await ctx.send("The queue is empty.")
        
        em = nextcord.Embed(title="Queue")
        
        queue = vc.queue.copy()
        songCount = 0
        for song in queue:
            songCount += 1
            em.add_field(name=f"Song Num {songCount}", value=f"`{song.title}`")
            
        await ctx.send(embed=em)

    @commands.command()
    async def volume(self, ctx: commands.Context, volume: int):
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Join a voice channel first.")
        else:
            vc: WavelinkPlayer = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send("No music is playing.")
        
        if volume > 100:
            return await ctx.send('Volume is too high.')
        elif volume < 0:
            return await ctx.send("Volume is too low.")
        # await ctx.send(f"Set the volume to `{volume}%`")
        return await vc.set_volume(volume)

    @commands.command()
    async def nowplaying(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Join a voice channel first.")
        else:
            vc: WavelinkPlayer = ctx.voice_client
        
        if not vc.is_playing(): 
            return await ctx.send("No music is playing.")

        em = nextcord.Embed(title=f"Now Playing: {vc.source.title}", description=f"Artist: {vc.source.author}")
        em.add_field(name="Duration", value=f"`{str(datetime.timedelta(seconds=vc.source.length))}`")
        em.add_field(name="Extra Info", value=f"Song URL: [Click Me]({str(vc.source.uri)})")
        em.set_thumbnail(url=vc.source.thumbnail)
        return await ctx.send(embed=em)

    @commands.command()
    async def splay(self, ctx: commands.Context, *, search: str):
        if not ctx.voice_client:
                vc: WavelinkPlayer = await ctx.author.voice.channel.connect(cls=WavelinkPlayer)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Join a voice channel first.")
        else:
            vc: WavelinkPlayer = ctx.voice_client
            
        if vc.queue.is_empty and not vc.is_playing():
            try:
                track = await spotify.SpotifyTrack.search(query=search, return_first=True)
                await vc.play(track)
                await ctx.send(f'Playing `{track.title}`')
            except Exception as e:
                await ctx.send("Please enter a Spotify **song URL**.")
                return print(e)
        else:
            await vc.queue.put_wait(search)
            await ctx.send(f'Added `{search.title}` to the queue...')
        vc.ctx = ctx
        try:
            if vc.loop: return
        except Exception:
            setattr(vc, "loop", False)

