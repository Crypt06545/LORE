import nextcord
import datetime
import random
import asyncio
from nextcord.ext import commands


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def convert(self, time):
        pos = ["s", "m", "h", "d"]
        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600*24}

        unit = time[-1]

        if unit not in pos:
            return -1
        try:
            val = int(time[:-1])
        except:
            return -2

        return val * time_dict[unit]

    @nextcord.slash_command(name="giveaway", description="Announce a giveaway")
    @commands.has_role("Giveaways")
    async def giveaway(self, ctx):
        await ctx.send("Let's start with this giveaway! Answer these questions within 15 seconds!")

        questions = [
            "Which channel should it be hosted in?",
            "What should be the duration of the giveaway? (s|m|h|d)",
            "What is the prize of the giveaway?"
        ]

        answers = []

        def check(m):
            return m.author == ctx.user and m.channel == ctx.channel

        for i in questions:
            await ctx.send(i)

            try:
                msg = await self.bot.wait_for('message', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send('You didn\'t answer in time, please be quicker next time!')
                return
            else:
                answers.append(msg.content)

        try:
            c_id = int(answers[0][2:-1])
        except:
            await ctx.send(f"You didn't mention a channel properly. Do it like this {ctx.channel.mention} next time.")
            return

        channel = self.bot.get_channel(c_id)

        time = self.convert(answers[1])
        if time == -1:
            await ctx.send(f"You didn't answer the time with a proper unit. Use (s|m|h|d) next time!")
            return
        elif time == -2:
            await ctx.send(f"The time must be an integer. Please enter an integer next time")
            return


        prize = answers[2]

        await ctx.send(f"The Giveaway will be in {channel.mention} and will last {answers[1]}!")

        end_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=time)
        embed = nextcord.Embed(
            title="🎉 Giveaway! 🎉",
            description=f"**Prize:** {prize}\n\n**Hosted by:** {ctx.user.mention}",
            color=nextcord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Ends At:", value=f"{end_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        embed.set_footer(text=f"Ends {answers[1]} from now! 🎉")

        my_msg = await channel.send(embed=embed)
        await my_msg.add_reaction("🎉")

        await asyncio.sleep(time)

        new_msg = await channel.fetch_message(my_msg.id)

        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))

        if not users:
            await channel.send("No valid entries, no winner could be determined!")
            return

        winner = random.choice(users)

        await channel.send(f"Congratulations! {winner.mention} won **{prize}**! 🎉")

    @commands.command()
    @commands.has_role("Giveaways")
    async def reroll(self, ctx, channel: nextcord.TextChannel, id_: int):
        try:
            new_msg = await channel.fetch_message(id_)
        except:
            await ctx.send("The id was entered incorrectly.")
            return

        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))

        if not users:
            await ctx.send("No valid entries, no winner could be determined!")
            return

        winner = random.choice(users)

        await channel.send(f"Congratulations! The new winner is {winner.mention}! 🎉")
