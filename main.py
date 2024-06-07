import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv
from commands.weather import Weather
from commands.about_dev import AboutDEV
from commands.welcome import MemberEvents
from commands.errorHandeller import On_Error
from commands.serverinfo import ServerInfo
from commands.kick import Kick
from commands.mute import Mute
from commands.unmute import UnMute
from commands.ping import Ping
from commands.meme import Meme
from commands.giveway import Giveaways
from commands.wanted import ImageCommands
from commands.waifu import Waifus
from commands.ban import Ban
from commands.unban import UnBan
from commands.clear import Clear
from commands.economy import Economy
from commands.slowmo import Slowmo
from commands.avatar import Avatar
from commands.help import Help
from commands.who import Who
from commands.snipe import Snipe
from commands.level import LevelSystem
from commands.afk import AFK
from commands.TicTac import TicTacToeCog
from commands.calculator import Calculator
from commands.rps import RPS
from commands.ImageAi import ImageGenerations
from commands.antiSpma import Antispam
from commands.censor import Censor
from commands.ticket import Ticket
# from commands.other import SettingsOther
from commands.anime import Anime
from commands.manga import Manga
from commands.connect4 import Connect4
from commands.hide import Hide
from commands.poll import Poll
from commands.warn import ModWarn
# from commands.suggestion import Suggestions
# from commands.music import Music
from alive import keep_alive  # Add this line

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = commands.Bot(command_prefix=[], intents=nextcord.Intents.all())
bot.remove_command("help")


@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")


bot.add_cog(Weather(bot))
bot.add_cog(AboutDEV(bot))
bot.add_cog(MemberEvents(bot))
bot.add_cog(On_Error(bot))
bot.add_cog(Kick(bot))
bot.add_cog(ServerInfo(bot))
bot.add_cog(Mute(bot))
bot.add_cog(UnMute(bot))
bot.add_cog(Ping(bot))
bot.add_cog(Ban(bot))
bot.add_cog(UnBan(bot))
bot.add_cog(Clear(bot))
bot.add_cog(Avatar(bot))
bot.add_cog(ImageCommands(bot))
bot.add_cog(Who(bot))
bot.add_cog(Slowmo(bot))
bot.add_cog(Waifus(bot))
bot.add_cog(Giveaways(bot))
bot.add_cog(AFK(bot))
bot.add_cog(Meme(bot))
bot.add_cog(Snipe(bot))
bot.add_cog(LevelSystem(bot))
bot.add_cog(Economy(bot))
bot.add_cog(Help(bot))
bot.add_cog(TicTacToeCog(bot))
bot.add_cog(Calculator(bot))
bot.add_cog(RPS(bot))
bot.add_cog(ImageGenerations(bot))
bot.add_cog(Antispam(bot))
bot.add_cog(Censor(bot))
bot.add_cog(Ticket(bot))
# bot.add_cog(SettingsOther(bot))
bot.add_cog(Connect4(bot))
bot.add_cog(Poll(bot))
bot.add_cog(Hide(bot))
bot.add_cog(ModWarn(bot))
bot.add_cog(Anime(bot))
bot.add_cog(Manga(bot))
# bot.add_cog(Suggestions(bot))
# bot.add_cog(Music(bot))

keep_alive()  # Add this line

bot.run(BOT_TOKEN)
