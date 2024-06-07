import nextcord
import random
import aiosqlite
from nextcord.ext import commands
from nextcord import Interaction
from easy_pil import Editor, Canvas, Font, load_image_async


class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.db = await aiosqlite.connect('db/level.db')
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS levels (
                user INTEGER NOT NULL,
                guild INTEGER NOT NULL,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                PRIMARY KEY (user, guild)
            )
        ''')

        # await cursor.execute("CREATE TABLE IF NOT EXISTS (levelsays BOOL, role)")


        await self.db.commit()

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return
        author = message.author
        guild = message.guild

        async with self.db.cursor() as cursor:
            await cursor.execute('SELECT xp, level FROM levels WHERE user = ? AND guild = ?', (author.id, guild.id))
            result = await cursor.fetchone()
            
            if result is None:
                xp, level = 0, 0
                await cursor.execute('INSERT INTO levels (user, guild, xp, level) VALUES (?, ?, ?, ?)', (author.id, guild.id, xp, level))
            else:
                xp, level = result
            
            xp += random.randint(1, 3)
            if xp >= 100:
                xp = 0
                level += 1
                await message.channel.send(f"{author.mention} has leveled up to level {level}")

            await cursor.execute('UPDATE levels SET xp = ?, level = ? WHERE user = ? AND guild = ?', (xp, level, author.id, guild.id))
            await self.db.commit()

    @nextcord.slash_command(name="level", description="Show a member's level")
    async def level(self, interaction: Interaction, member: nextcord.Member = None):
        if member is None:
            member = interaction.user

        async with self.db.cursor() as cursor:
            await cursor.execute('SELECT xp, level FROM levels WHERE user = ? AND guild = ?', (member.id, interaction.guild.id))
            result = await cursor.fetchone()

            if result is None:
                xp, level = 0, 0
            else:
                xp, level = result

        user_data = {
            "xp": xp,
            "name": f"{member.name}",
            "level": level,
            "next_level_xp": 100,
            "percentage": xp,
        }

        background = Editor(Canvas((900, 300), color="#1c1c1c"))
        profile_picture = await load_image_async(str(member.avatar.url))
        profile = Editor(profile_picture).resize((150, 150)).circle_image()

        poppins = Font.poppins(size=40)
        poppins_small = Font.poppins(size=30)

        card_right_shape = [(600, 0), (750, 300), (900, 300), (900, 0)]

        background.polygon(card_right_shape, color="#2c2c2c")
        background.paste(profile, (30, 30))

        background.rectangle((30, 220), width=650, height=40, color="#2c2c2c", radius=20)
        background.bar((30, 220), max_width=650, height=40, percentage=user_data["percentage"], color="#7289da", radius=20)
        background.text((200, 40), user_data["name"], font=poppins, color="#FFFFFF")

        background.rectangle((200, 100), width=350, height=2, fill="#FFFFFF")
        background.text(
            (200, 130),
            f"Level - {user_data['level']} | XP - {user_data['xp']}/{user_data['next_level_xp']}",
            font=poppins_small,
            color="#FFFFFF",
        )

        file = nextcord.File(fp=background.image_bytes, filename="levelcard.png")
        await interaction.response.send_message(file=file)
