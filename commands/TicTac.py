from typing import List
from nextcord.ext import commands
import nextcord
from nextcord import Interaction, Member
from dotenv import load_dotenv
import os

load_dotenv()
GUILD_ID = int(os.getenv("GUILD_ID"))

class TicTacToeButton(nextcord.ui.Button['TicTacToeView']):
    def __init__(self, x: int, y: int):
        super().__init__(style=nextcord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: Interaction):
        global player1
        global player2
        assert self.view is not None
        view: TicTacToeView = self.view
        state = view.board[self.y][self.x]
        
        if state in (view.X, view.O):
            return

        content = ""  # Initialize content

        if view.current_player == view.X:
            if interaction.user != player1:
                await interaction.response.send_message("It's not your Turn!", ephemeral=True)
                return
            else:
                self.style = nextcord.ButtonStyle.danger
                self.label = 'X'
                self.disabled = True
                view.board[self.y][self.x] = view.X
                view.current_player = view.O
                content = f"It is now {player2.mention}'s turn **O**"
        else:
            if interaction.user != player2:
                await interaction.response.send_message("It's not your Turn!", ephemeral=True)
                return
            else:
                self.style = nextcord.ButtonStyle.success
                self.label = 'O'
                self.disabled = True
                view.board[self.y][self.x] = view.O
                view.current_player = view.X
                content = f"It is now {player1.mention}'s turn **X**"
        
        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f'{player1.mention} **X** won!'
            elif winner == view.O:
                content = f'{player2.mention} **O** won!'
            else:
                content = "It's a tie!"
            for child in view.children:
                child.disabled = True
            view.stop()

        await interaction.response.edit_message(content=content, view=view)

class TicTacToeView(nextcord.ui.View):
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2
    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X
        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X
        if all(i != 0 for row in self.board for i in row):
            return self.Tie
        return None

class TicTacToeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("TicTacToe is online.")

    @nextcord.slash_command(name="tictactoe", description="Play TicTacToe.",guild_ids=[GUILD_ID])
    async def tictactoe(self, interaction: Interaction, enemy: Member):
        await interaction.response.send_message(f"Tic Tac Toe: {interaction.user.mention} goes first **X**", view=TicTacToeView())
        global player1, player2
        player1 = interaction.user
        player2 = enemy


