from nextcord.ext import commands
import nextcord
from nextcord import Interaction, Embed
from nextcord.ui import View, Button
from datetime import datetime, timedelta



class CalcButton(Button):
    def __init__(self, label, style, row, calculator):
        super().__init__(label=label, style=style, row=row)
        self.calculator = calculator

    async def callback(self, interaction: Interaction):
        await self.calculator.handle_button_click(interaction, self.label)


class Calculator(commands.Cog):
    def __init__(self, client):
        self.client = client

    def create_buttons(self):
        buttons = [
            [
                CalcButton(label="1", style=nextcord.ButtonStyle.grey, row=0, calculator=self),
                CalcButton(label="2", style=nextcord.ButtonStyle.grey, row=0, calculator=self),
                CalcButton(label="3", style=nextcord.ButtonStyle.grey, row=0, calculator=self),
                CalcButton(label="×", style=nextcord.ButtonStyle.blurple, row=0, calculator=self),
                CalcButton(label="Exit", style=nextcord.ButtonStyle.danger, row=0, calculator=self),
            ],
            [
                CalcButton(label="4", style=nextcord.ButtonStyle.grey, row=1, calculator=self),
                CalcButton(label="5", style=nextcord.ButtonStyle.grey, row=1, calculator=self),
                CalcButton(label="6", style=nextcord.ButtonStyle.grey, row=1, calculator=self),
                CalcButton(label="÷", style=nextcord.ButtonStyle.blurple, row=1, calculator=self),
                CalcButton(label="⌫", style=nextcord.ButtonStyle.danger, row=1, calculator=self),
            ],
            [
                CalcButton(label="7", style=nextcord.ButtonStyle.grey, row=2, calculator=self),
                CalcButton(label="8", style=nextcord.ButtonStyle.grey, row=2, calculator=self),
                CalcButton(label="9", style=nextcord.ButtonStyle.grey, row=2, calculator=self),
                CalcButton(label="+", style=nextcord.ButtonStyle.blurple, row=2, calculator=self),
                CalcButton(label="Clear", style=nextcord.ButtonStyle.danger, row=2, calculator=self),
            ],
            [
                CalcButton(label="00", style=nextcord.ButtonStyle.grey, row=3, calculator=self),
                CalcButton(label="0", style=nextcord.ButtonStyle.grey, row=3, calculator=self),
                CalcButton(label=".", style=nextcord.ButtonStyle.grey, row=3, calculator=self),
                CalcButton(label="-", style=nextcord.ButtonStyle.blurple, row=3, calculator=self),
                CalcButton(label="=", style=nextcord.ButtonStyle.success, row=3, calculator=self),
            ],
        ]
        return buttons

    def calculator(self, exp):
        exp = exp.replace('×', '*').replace('÷', '/')
        try:
            return str(eval(exp))
        except:
            return 'An error occurred'

    async def handle_button_click(self, interaction: Interaction, label: str):
        embed = interaction.message.embeds[0]
        expression = embed.description if embed.description != 'None' else ''
        
        if label == "Exit":
            await interaction.response.edit_message(content='Calculator closed', view=None, embed=None)
            return
        elif label == '⌫':
            expression = expression[:-1]
        elif label == 'Clear':
            expression = 'None'
        elif label == '=':
            expression = self.calculator(expression)
        else:
            expression += label

        embed.description = expression
        await interaction.response.edit_message(embed=embed)

    @nextcord.slash_command(name="calc", description="Open a calculator")
    async def calc(self, interaction: Interaction):
        user = interaction.user
        expression = 'None'
        delta = datetime.utcnow() + timedelta(minutes=5)
        embed = Embed(title=f'{user.name}\'s Calculator', description=expression, timestamp=delta)
        view = self.create_view()

        await interaction.send(embed=embed, view=view)

    def create_view(self):
        view = View()
        buttons = self.create_buttons()
        for row in buttons:
            for button in row:
                view.add_item(button)
        return view


