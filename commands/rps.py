import nextcord
from nextcord import slash_command
from nextcord.ext import commands
import random
import asyncio


class Player1Buttons(nextcord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @nextcord.ui.button(label="Rock", style=nextcord.ButtonStyle.blurple, emoji="🪨")
    async def p1_rock(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != player1:
            await interaction.response.send_message("> This is not your turn/game!", ephemeral=True)
        else:
            global player1_choice
            player1_choice = "rock 🪨"
            if enemy is None or enemy == playerbot:
                comp_choice = random.choice(rpsGame)
                if comp_choice == 'rock 🪨':
                    await interaction.response.send_message(f'Well, that was weird. We tied.\n>>> Your choice: **{player1_choice}**\nMy choice: **{comp_choice}**', view=playAgain())
                elif comp_choice == 'paper 🧻':
                    await interaction.response.send_message(f'Nice try, but I won this time!!\n>>> Your choice: **{player1_choice}**\nMy choice: **{comp_choice}**', view=playAgain())
                elif comp_choice == 'scissors ✂️':
                    await interaction.response.send_message(f"Aw, you beat me. It won't happen again!\n>>> Your choice: **{player1_choice}**\nMy choice: **{comp_choice}**", view=playAgain())
                for child in self.children:
                    child.disabled = True
                await interaction.message.edit(view=self)
            else:
                # player 2 msg
                view = Player2Buttons()
                embed = nextcord.Embed(description=f"Waiting for **{enemy.name}** choice..\nRock, paper, or scissors? Choose wisely...")
                await interaction.message.edit(content=f"{enemy.mention}'s turn", embed=embed, view=view)
                await interaction.response.defer()

    @nextcord.ui.button(label="Paper", style=nextcord.ButtonStyle.blurple, emoji="🧻")
    async def p1_paper(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != player1:
            await interaction.response.send_message("> This is not your turn/game!", ephemeral=True)
        else:
            global player1_choice
            player1_choice = "paper 🧻"
            if enemy is None or enemy == playerbot:
                comp_choice = random.choice(rpsGame)
                if comp_choice == 'rock 🪨':
                    await interaction.response.send_message(f'Aw man, you actually managed to beat me.\n>>> Your choice: **{player1_choice}**\nMy choice: **{comp_choice}**', view=playAgain())
                elif comp_choice == 'paper 🧻':
                    await interaction.response.send_message(f'Oh, wacky. We just tied. I call a rematch!!\n>>> Your choice: **{player1_choice}**\nMy choice: **{comp_choice}**', view=playAgain())
                elif comp_choice == 'scissors ✂️':
                    await interaction.response.send_message(f"I WON!!!\n>>> Your choice: **{player1_choice}**\nMy choice: **{comp_choice}**", view=playAgain())
                for child in self.children:
                    child.disabled = True
                await interaction.message.edit(view=self)
            else:
                # player 2 msg
                view = Player2Buttons()
                embed = nextcord.Embed(description=f"Waiting for **{enemy.name}** choice..\nRock, paper, or scissors? Choose wisely...")
                await interaction.message.edit(content=f"{enemy.mention}'s turn", embed=embed, view=view)
                await interaction.response.defer()

    @nextcord.ui.button(label="Scissors", style=nextcord.ButtonStyle.blurple, emoji="✂️")
    async def p1_scissors(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != player1:
            await interaction.response.send_message("> This is not your turn/game!", ephemeral=True)
        else:
            global player1_choice
            player1_choice = "scissors ✂️"
            if enemy is None or enemy == playerbot:
                comp_choice = random.choice(rpsGame)
                if comp_choice == 'rock 🪨':
                    await interaction.response.send_message(f'HAHA!! I JUST CRUSHED YOU!! I rock!!\n>>> Your choice: **{player1_choice}**\nMy choice: **{comp_choice}**', view=playAgain())
                elif comp_choice == 'paper 🧻':
                    await interaction.response.send_message(f'Bruh. >: |\n>>> Your choice: **{player1_choice}**\nMy choice: **{comp_choice}**', view=playAgain())
                elif comp_choice == 'scissors ✂️':
                    await interaction.response.send_message(f"Oh well, we tied.\n>>> Your choice: **{player1_choice}**\nMy choice: **{comp_choice}**", view=playAgain())
                for child in self.children:
                    child.disabled = True
                await interaction.message.edit(view=self)
            else:
                # player 2 msg
                view = Player2Buttons()
                embed = nextcord.Embed(description=f"Waiting for **{enemy.name}** choice..\nRock, paper, or scissors? Choose wisely...")
                await interaction.message.edit(content=f"{enemy.mention}'s turn", embed=embed, view=view)
                await interaction.response.defer()

class Player2Buttons(nextcord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @nextcord.ui.button(label="Rock", style=nextcord.ButtonStyle.blurple, emoji="🪨")
    async def p2_rock(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != enemy:
            await interaction.response.send_message("> This is not your turn/game!", ephemeral=True)
        else:
            global player2_choice
            player2_choice = "rock 🪨"
            if player1_choice == 'rock 🪨':
                await interaction.response.send_message(f'Well, that was weird. Both of you tied.\n>>> {player1.mention} choice: **{player1_choice}**\n{enemy.mention} choice: **{player2_choice}**', view=playAgain())
            elif player1_choice == 'paper 🧻':
                await interaction.response.send_message(f'The pen beats the sword? More like the paper beats the rock!!\n>>> {player1.mention} choice: **{player1_choice}**\n{enemy.mention} choice: **{player2_choice}**', view=playAgain())
            elif player1_choice == 'scissors ✂️':
                await interaction.response.send_message(f'HAHA!! **{enemy.name}** JUST CRUSHED **{player1.name}**!!\n>>> {player1.mention} choice: **{player1_choice}**\n{enemy.mention} choice: **{player2_choice}**', view=playAgain())
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)

    @nextcord.ui.button(label="Paper", style=nextcord.ButtonStyle.blurple, emoji="🧻")
    async def p2_paper(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != enemy:
            await interaction.response.send_message("> This is not your turn/game!", ephemeral=True)
        else:
            global player2_choice
            player2_choice = "paper"
            if player1_choice == 'rock 🪨':
                await interaction.response.send_message(f'Nice try **{player1.name}**, but **{enemy.name}** won this time!!\n>>> {player1.mention} choice: **{player1_choice}**\n{enemy.mention} choice: **{player2_choice}**', view=playAgain())
            elif player1_choice == 'paper 🧻':
                await interaction.response.send_message(f'Oh, wacky. you just tied. I call a rematch!!\n>>> {player1.mention} choice: **{player1_choice}**\n{enemy.mention} choice: **{player2_choice}**', view=playAgain())
            elif player1_choice == 'scissors ✂️':
                await interaction.response.send_message(f'Bruh. >: |\n>>> **{player1.name}** choice: **{player1_choice}**\n{enemy.mention} choice: **{player2_choice}**', view=playAgain())
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)

    @nextcord.ui.button(label="Scissors", style=nextcord.ButtonStyle.blurple, emoji="✂️")
    async def p2_scissors(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != enemy:
            await interaction.response.send_message("> This is not your turn/game!", ephemeral=True)
        else:
            global player2_choice
            player2_choice = "scissors ✂️"
            if player1_choice == 'rock 🪨':
                await interaction.response.send_message(f"Aw, **{player1.name}** beat **{enemy.name}**. Hard luck **{enemy.name}**!\n>>> {player1.mention} choice: **{player1_choice}**\n{enemy.mention} choice: **{player2_choice}**", view=playAgain())
            elif player1_choice == 'paper 🧻':
                await interaction.response.send_message(f"Aw man, **{enemy.name}** actually managed to beat **{player1.name}**.\n>>> {player1.mention} choice: **{player1_choice}**\n{enemy.mention} choice: **{player2_choice}**", view=playAgain())
            elif player1_choice == 'scissors ✂️':
                await interaction.response.send_message(f"Oh well, you tied.\n>>> {player1.mention} choice: **{player1_choice}**\n{enemy.mention} choice: **{player2_choice}**", view=playAgain())
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)

class playAgain(nextcord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @nextcord.ui.button(label="Play Again", style=nextcord.ButtonStyle.green)
    async def play_again(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != player1:
            await interaction.response.send_message("> Only player 1 can click the button", ephemeral=True)
        else:
            if enemy is None or enemy == playerbot:
                view = Player1Buttons()
                embed = nextcord.Embed(description="Rock, paper, or scissors? Choose wisely...", color=0x2F3136)
                await interaction.response.send_message(embed=embed, view=view)
            elif enemy.bot:
                return await interaction.response.send_message("> You can play with me or with another member. Not another bot!", ephemeral=True)
            else:
                # player 1 msg
                view = Player1Buttons()
                embed = nextcord.Embed(description=f"Waiting for **{player1.name}** choice..\nRock, paper, or scissors? Choose wisely...")
                await interaction.response.send_message(f"{player1.mention}'s turn", embed=embed, view=view)
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)

class RPS(commands.Cog):
    GAME_TIMEOUT_THRESHOLD = 180
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("RPS is online.")

    @slash_command(name="rps", description="Play Rock Paper Scissors.")
    async def rps(self, interaction: nextcord.Interaction, player2: nextcord.Member = None):
        global enemy, player1, rpsGame, playerbot
        playerbot = self.bot.user
        player1 = interaction.user
        enemy = player2
        rpsGame = ['rock 🪨', 'paper 🧻', 'scissors ✂️']
        if player2 == player1:
            return await interaction.response.send_message(">>> You can not play with yourself!\nYou can play with me if you are that lonely...", ephemeral=True)
        elif player2 is None or player2 == self.bot.user:
            view = Player1Buttons()
            embed = nextcord.Embed(description="Rock, paper, or scissors? Choose wisely...", color=0x2F3136)
            await interaction.response.send_message(embed=embed, view=view)
            try:
                await self.bot.wait_for('interaction', check=lambda interaction: interaction.data["component_type"] == 2 and "custom_id" in interaction.data.keys(), timeout=self.GAME_TIMEOUT_THRESHOLD)
            except asyncio.TimeoutError:
                await interaction.followup.send(f"> {player1.mention} ran out of time and lost.")
        elif player2.bot:
            return await interaction.response.send_message("> You can play with me or with another member. Not another bot!", ephemeral=True)
        else:
            view = Player1Buttons()
            embed = nextcord.Embed(description=f"Waiting for **{player1.name}** choice..\nRock, paper, or scissors? Choose wisely...")
            await interaction.response.send_message(f"{player1.mention}'s turn", embed=embed, view=view)
            try:
                await self.bot.wait_for('interaction', check=lambda interaction: interaction.data["component_type"] == 2 and "custom_id" in interaction.data.keys(), timeout=self.GAME_TIMEOUT_THRESHOLD)
            except asyncio.TimeoutError:
                await interaction.followup.send(f"> {player1.mention} ran out of time and lost.")
