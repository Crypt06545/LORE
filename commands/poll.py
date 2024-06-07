import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import aiosqlite
import ast



# poll buttons
class pollButtons(nextcord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)
        
    @nextcord.ui.button(label="Yes", style=nextcord.ButtonStyle.blurple, emoji="<:pepeyes:1070834912782987424>", custom_id="poll_yes_button")
    async def poll_yes_button(self,  button: nextcord.ui.Button, interaction: Interaction):
        # Fetching poll data...
        async with aiosqlite.connect("db/polls.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM polls WHERE poll_id = ?", (interaction.message.id,))
                data = await cursor.fetchone()
                poll_title = data[1]
                poll_description = data[2]
                poll_author = data[3]
                poll_avatar = data[4]
                upvotes = data[5]
                downvotes = data[6]
                upvote_users = ast.literal_eval(data[7])
                downvote_users = ast.literal_eval(data[8])

                if interaction.user.id in upvote_users:
                    upvotes -= 1
                    upvote_users.remove(interaction.user.id)
                    await cursor.execute("UPDATE polls SET upvotes = ?, upvote_users = ? WHERE poll_id = ?", (upvotes, str(upvote_users), interaction.message.id,))
                    await interaction.response.send_message("Vote removed.", ephemeral=True)
                elif interaction.user.id in downvote_users:
                    downvotes -= 1
                    downvote_users.remove(interaction.user.id)
                    upvotes += 1
                    upvote_users.append(interaction.user.id)
                    await cursor.execute("UPDATE polls SET upvotes = ?, upvote_users = ?, downvotes = ?, downvote_users = ? WHERE poll_id = ?", (upvotes, str(upvote_users), downvotes, str(downvote_users), interaction.message.id,))
                    await interaction.response.send_message("Voted.", ephemeral=True)
                else:
                    upvotes += 1
                    upvote_users.append(interaction.user.id)
                    await cursor.execute("UPDATE polls SET upvotes = ?, upvote_users = ? WHERE poll_id = ?", (upvotes, str(upvote_users), interaction.message.id,))
                    await interaction.response.send_message("Voted.", ephemeral=True)
                await db.commit()
                
        emb = nextcord.Embed(title=poll_title, description=poll_description)
        if poll_avatar != "no avatar":
            emb.set_author(name=f"Poll by {poll_author}", icon_url=poll_avatar)
        else:
            emb.set_author(name=f"Poll by {poll_author}")
        emb.set_footer(text=f"{upvotes} Yes | {downvotes} No")
        view = pollButtons()
        await interaction.message.edit(embed=emb, view=view)

    # no button
    @nextcord.ui.button(label="No", style=nextcord.ButtonStyle.blurple, emoji="<:pepeno:1070834894537773087>", custom_id="poll_no_button")
    async def poll_no_button(self,  button: nextcord.ui.Button,interaction: Interaction):
        # Fetching poll data...
        async with aiosqlite.connect("db/polls.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM polls WHERE poll_id = ?", (interaction.message.id,))
                data = await cursor.fetchone()
                poll_title = data[1]
                poll_description = data[2]
                poll_author = data[3]
                poll_avatar = data[4]
                upvotes = data[5]
                downvotes = data[6]
                upvote_users = ast.literal_eval(data[7])
                downvote_users = ast.literal_eval(data[8])

                if interaction.user.id in downvote_users:
                    downvotes -= 1
                    downvote_users.remove(interaction.user.id)
                    await cursor.execute("UPDATE polls SET downvotes = ?, downvote_users = ? WHERE poll_id = ?", (downvotes, str(downvote_users), interaction.message.id,))
                    await interaction.response.send_message("Vote removed.", ephemeral=True)
                elif interaction.user.id in upvote_users:
                    upvotes -= 1
                    upvote_users.remove(interaction.user.id)
                    downvotes += 1
                    downvote_users.append(interaction.user.id)
                    await cursor.execute("UPDATE polls SET downvotes = ?, downvote_users = ?, upvotes = ?, upvote_users = ? WHERE poll_id = ?", (downvotes, str(downvote_users), upvotes, str(upvote_users), interaction.message.id,))
                    await interaction.response.send_message("Voted.", ephemeral=True)
                else:
                    downvotes += 1
                    downvote_users.append(interaction.user.id)
                    await cursor.execute("UPDATE polls SET downvotes = ?, downvote_users = ? WHERE poll_id = ?", (downvotes, str(downvote_users), interaction.message.id,))
                    await interaction.response.send_message("Voted.", ephemeral=True)
                await db.commit()
                
        emb = nextcord.Embed(title=poll_title, description=poll_description)
        if poll_avatar != "no avatar":
            emb.set_author(name=f"Poll by {poll_author}", icon_url=poll_avatar)
        else:
            emb.set_author(name=f"Poll by {poll_author}")
        emb.set_footer(text=f"{upvotes} Yes | {downvotes} No")
        view = pollButtons()
        await interaction.message.edit(embed=emb, view=view)

# Poll Class
class Poll(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # wakin~
    @commands.Cog.listener()
    async def on_ready(self):
        print("Poll is online.")

    # poll command
    @nextcord.slash_command(name="poll", description="Make a poll.")
    async def poll(self, interaction: Interaction, title: str = SlashOption(description="The title of the poll."), description: str = SlashOption(description="The description of the poll.")):
        try:
            user_avatar = interaction.user.avatar.url
        except:
            user_avatar = "no avatar"
        view = pollButtons()
        emb = nextcord.Embed(title=title, description=description)
        if user_avatar != "no avatar":
            emb.set_author(name=f"Poll by {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
        else:
            emb.set_author(name=f"Poll by {interaction.user.display_name}")
        emb.set_footer(text="0 Yes | 0 No")
        await interaction.response.send_message("Poll Created!", ephemeral=True)
        poll_msg = await interaction.channel.send(embed=emb, view=view)
        async with aiosqlite.connect("db/polls.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS polls (poll_id INTEGER, poll_title TEXT, poll_description TEXT, poll_author TEXT, poll_avatar TEXT, upvotes INTEGER, downvotes INTEGER, upvote_users TEXT, downvote_users TEXT)")
                await cursor.execute("INSERT INTO polls (poll_id, poll_title, poll_description, poll_author, poll_avatar, upvotes, downvotes, upvote_users, downvote_users) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (poll_msg.id, title, description, interaction.user.display_name, user_avatar, 0, 0, "[]", "[]"))
                await db.commit()

