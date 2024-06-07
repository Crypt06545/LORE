import nextcord
from nextcord.ext import commands
import random
import json
import os


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    mainshop = [
        {"name": "⌚ Watch", "price": 100, "description": "Time"},
        {"name": "💻 Laptop", "price": 1000, "description": "Work"},
        {"name": "🖥️ PC", "price": 10000, "description": "Gaming"},
        {"name": "🎮 Game Console", "price": 5000, "description": "Entertainment"},
        {"name": "📱 Smartphone", "price": 800, "description": "Communication"},
        {"name": "📺 Television", "price": 2000, "description": "Entertainment"},
        {"name": "🎧 Headphones", "price": 300, "description": "Music"},
        {"name": "📚 Book", "price": 20, "description": "Knowledge"},
        {"name": "🚲 Bike", "price": 400, "description": "Transport"},
        {"name": "📷 Camera", "price": 1500, "description": "Photography"}
    ]

    @nextcord.slash_command(name="shop", description="View the shop")
    async def shop(self, interaction: nextcord.Interaction):
        em = nextcord.Embed(title="Shop", color=nextcord.Color.blurple())

        for item in self.mainshop:
            name = item["name"]
            price = item["price"]
            desc = item["description"]
            em.add_field(name=name, value=f"**Price:** ${price}\n**Description:** {desc}", inline=True)

        em.set_footer(text="Use the item name to buy, e.g., /buy Watch")
        await interaction.response.send_message(embed=em)


    @nextcord.slash_command(name="bag", description="View your bag")
    async def bag(self, interaction: nextcord.Interaction):
        await self.open_account(interaction.user)
        user = interaction.user
        users = await self.get_bank_data()

        try:
            bag = users[str(user.id)]["bag"]
        except KeyError:
            bag = []

        em = nextcord.Embed(title="Bag")
        for item in bag:
            name = item["item"]
            amount = item["amount"]
            em.add_field(name=name, value=amount)

        await interaction.response.send_message(embed=em)

    

    @nextcord.slash_command(name="buy", description="Buy an item from the shop")
    async def buy(self, interaction: nextcord.Interaction, item: str, amount: int = 1):
        await self.open_account(interaction.user)
        res = await self.buy_this(interaction.user, item, amount)
        if not res[0]:
            if res[1] == 1:
                await interaction.response.send_message("That item isn't available!")
                return
            if res[1] == 2:
                await interaction.response.send_message(f"You don't have enough money to buy {amount} {item}!")
                return
        await interaction.response.send_message(f"You just bought {amount} {item}")

        
    async def buy_this(self, user, item_name, amount):
        item_name = item_name.lower()
        name_ = None
        for item in self.mainshop:
            name = item["name"].lower().split(' ', 1)[1]  # Ignore emoji for comparison
            if name == item_name:
                name_ = item["name"]
                price = item["price"]
                break

        if name_ is None:
            return [False, 1]

        cost = price * amount

        users = await self.get_bank_data()

        bal = await self.update_bank(user)

        if bal[0] < cost:
            return [False, 2]

        try:
            index = 0
            t = None
            for thing in users[str(user.id)]["bag"]:
                n = thing["item"]
                if n == name_:
                    old_amt = thing["amount"]
                    new_amt = old_amt + amount
                    users[str(user.id)]["bag"][index]["amount"] = new_amt
                    t = 1
                    break
                index += 1
            if t is None:
                obj = {"item": name_, "amount": amount}
                users[str(user.id)]["bag"].append(obj)
        except KeyError:
            obj = {"item": name_, "amount": amount}
            users[str(user.id)]["bag"] = [obj]

        with open("mainbank.json", "w") as f:
            json.dump(users, f)

        await self.update_bank(user, cost * -1, "wallet")

        return [True, "Worked"]
    
    @nextcord.slash_command(name="sell", description="Sell an item from your bag")
    async def sell(self, interaction: nextcord.Interaction, item: str, amount: int = 1):
        await self.open_account(interaction.user)

        res = await self.sell_this(interaction.user, item, amount)

        if not res[0]:
            if res[1] == 1:
                await interaction.response.send_message("That item isn't available!")
                return
            if res[1] == 2:
                await interaction.response.send_message(f"You don't have {amount} {item} in your bag.")
                return
            if res[1] == 3:
                await interaction.response.send_message(f"You don't have {item} in your bag.")
                return

        await interaction.response.send_message(f"You just sold {amount} {item}.")

    async def sell_this(self, user, item_name, amount, price=None):
        item_name = item_name.lower()
        name_ = None
        for item in self.mainshop:
            name = item["name"].lower().split(' ', 1)[1]  # Ignore emoji for comparison
            if name == item_name:
                name_ = item["name"]
                if price is None:
                    price = 0.9 * item["price"]
                break

        if name_ is None:
            return [False, 1]

        cost = price * amount

        users = await self.get_bank_data()

        bal = await self.update_bank(user)

        try:
            index = 0
            t = None
            for thing in users[str(user.id)]["bag"]:
                n = thing["item"]
                if n == name_:
                    old_amt = thing["amount"]
                    if old_amt < amount:
                        return [False, 2]  # Not enough items in the bag
                    new_amt = old_amt - amount
                    if new_amt == 0:
                        users[str(user.id)]["bag"].pop(index)  # Remove item from bag if the amount becomes zero
                    else:
                        users[str(user.id)]["bag"][index]["amount"] = new_amt
                    t = 1
                    break
                index += 1
            if t is None:
                return [False, 3]  # Item not found in bag
        except KeyError:
            return [False, 3]  # Bag not found for the user

        with open("mainbank.json", "w") as f:
            json.dump(users, f)

        await self.update_bank(user, cost, "wallet")  # Add money to wallet upon selling

        return [True, "Worked"]


    @nextcord.slash_command(name="balance", description="Check your balance")
    async def balance(self, interaction: nextcord.Interaction):
        await self.open_account(interaction.user)  
        users = await self.get_bank_data()

        wallet_amt = users[str(interaction.user.id)]["wallet"]
        bank_amt = users[str(interaction.user.id)]["bank"]
        
        em = nextcord.Embed(title=f"{interaction.user.name}'s Balance", color=nextcord.Color.red())
        em.add_field(name="Wallet Balance :coin:", value=wallet_amt)
        em.add_field(name="Bank Balance :coin:", value=bank_amt)
        await interaction.response.send_message(embed=em)

    @nextcord.slash_command(name="beg", description="Beg for coins")
    async def beg(self, interaction: nextcord.Interaction):
        await self.open_account(interaction.user)
        users = await self.get_bank_data()
        earnings = random.randrange(10)

        await interaction.response.send_message(f"You received {earnings} :coin: coins by begging!")

        users[str(interaction.user.id)]["wallet"] += earnings
        await self.save_bank_data(users)
        
    @nextcord.slash_command(name="withdraw", description="Withdraw coins from bank")
    async def withdraw(self, interaction: nextcord.Interaction, amount: int):
        await self.open_account(interaction.user)
        if amount is None:
            await interaction.response.send_message("Please enter the amount.")
            return
            
        bal = await self.update_bank(interaction.user)

        if amount > bal[1]:  # Check bank balance
            await interaction.response.send_message("You don't have that much money in your bank!")
            return

        if amount <= 0:
            await interaction.response.send_message("Amount must be positive!")
            return
        
        await self.update_bank(interaction.user, -amount, "bank")
        await self.update_bank(interaction.user, amount, "wallet")

        await interaction.response.send_message(f"You withdrew {amount} :coin: coins from your bank!")

    @nextcord.slash_command(name="deposit", description="Deposit coins into bank")
    async def deposit(self, interaction: nextcord.Interaction, amount: int):
        await self.open_account(interaction.user)
        if amount is None:
            await interaction.response.send_message("Please enter the amount :coin: !")
            return
            
        bal = await self.update_bank(interaction.user)

        if amount > bal[0]:  # Check wallet balance
            await interaction.response.send_message("You don't have that much money in your wallet!")
            return

        if amount <= 0:
            await interaction.response.send_message("Amount must be positive!")
            return
        
        await self.update_bank(interaction.user, -amount, "wallet")
        await self.update_bank(interaction.user, amount, "bank")

        await interaction.response.send_message(f"You deposited {amount} :coin: coins into your bank!")

    @nextcord.slash_command(name="slots", description="Play a slots game")
    async def slots(self, interaction: nextcord.Interaction, amount: int):
        await self.open_account(interaction.user)
        if amount is None:
            await interaction.response.send_message("Please enter the amount.")
            return
        bal = await self.update_bank(interaction.user)
        if amount > bal[0]:
            await interaction.response.send_message("You don't have that much money in your wallet!")
            return
        if amount <= 0:
            await interaction.response.send_message("Amount must be positive!")
            return

        final = []
        for i in range(3):
            emoji = random.choice(["🍓", "💸", "🍍"])
            final.append(emoji)
        await interaction.response.send_message(' '.join(final))

        if final[0] == final[1] == final[2]:
            await self.update_bank(interaction.user, 2 * amount)
            result_message = "You won! 🎉"
        else:
            await self.update_bank(interaction.user, -amount)
            result_message = "You lost! 😔"

        bal = await self.update_bank(interaction.user)
        wallet_balance = bal[0]

        await interaction.response.send_message(f"{result_message} - Your current wallet balance: {wallet_balance} :coin:")

    @nextcord.slash_command(name="send", description="Send coins to another user")
    async def send(self, interaction: nextcord.Interaction, member: nextcord.Member, amount: int):
        await self.open_account(interaction.user)
        await self.open_account(member)

        if amount is None:
            await interaction.response.send_message("Please enter a valid amount.")
            return

        try:
            amount = int(amount)
        except ValueError:
            await interaction.response.send_message("Please enter a valid amount (numbers only).")
            return

        bal = await self.update_bank(interaction.user)
        if amount > bal[0]:  # Check wallet balance
            await interaction.response.send_message("You don't have that much money!")
            return

        if amount <= 0:
            await interaction.response.send_message("Amount must be positive!")
            return

        await self.update_bank(interaction.user, -amount, "wallet")
        await self.update_bank(member, amount, "wallet")

        await interaction.response.send_message(f"You gave **{amount}** :coin: coins to {member.mention}!")

    @nextcord.slash_command(name="rob", description="Rob another user")
    async def rob(self, interaction: nextcord.Interaction, member: nextcord.Member):
        await self.open_account(interaction.user)
        await self.open_account(member)

        target_bal = await self.update_bank(member)
        if target_bal[0] < 100:
            await interaction.response.send_message("It's not worth it!")
            return

        earnings = random.randint(0, min(100, target_bal[0]))

        await self.update_bank(interaction.user, earnings, "wallet")
        await self.update_bank(member, -earnings, "wallet")

        await interaction.response.send_message(f"You robbed and got {earnings} :coin: coins from {member.mention}!")

    async def open_account(self, user):
        users = await self.get_bank_data()
        if str(user.id) not in users:
            users[str(user.id)] = {"wallet": 0, "bank": 0, "bag": []}
            await self.save_bank_data(users)

    async def get_bank_data(self):
        if not os.path.exists("mainbank.json"):
            with open("mainbank.json", "w") as f:
                json.dump({}, f)
        with open("mainbank.json", "r") as f:
            users = json.load(f)
        return users

    async def save_bank_data(self, users):
        with open("mainbank.json", "w") as f:
            json.dump(users, f)
    
    async def update_bank(self, user, change=0, mode="wallet"):
        users = await self.get_bank_data()
        users[str(user.id)][mode] += change
        with open("mainbank.json", 'w') as f:
            json.dump(users, f)
        bal = [users[str(user.id)]["wallet"], users[str(user.id)]["bank"]]
        return bal

