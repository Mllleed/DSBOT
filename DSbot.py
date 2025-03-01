import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from languages import translations

# from database import log_action, create_table

# Загружаем переменные окружения
load_dotenv()

# Токен и ID сервера
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

# Устанавливаем интенты
intents = discord.Intents.default()
intents.guilds = True
intents.reactions = True
intents.typing = True
intents.voice_states = True
intents.presences = True
intents.members = True
intents.message_content = True

# Префикс команд
bot = commands.Bot(command_prefix="!", intents=intents)
bot2 = commands.Bot(command_prefix="?", intents=intents)

# Очередь для передачи данных между ботами
queue = asyncio.Queue()


@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} запущен и подключен к серверу!")
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f"👥 Число участников на сервере: {len(guild.members)}")
    else:
        print("❌ Бот не подключен к серверу или ID неверен")
    bot.loop.create_task(process_queue())


async def check_discord_user(username):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("❌ Ошибка: Бот не находится на сервере с указанным ID")
        return None

    username_lower = username.lower()
    print(f"🔍 Ищу пользователя: {username}")
    
    for member in guild.members:
        if member.name.lower() == username_lower or member.display_name.lower() == username_lower:
            print(f"✅ Найден: {member.name}")
            return member
    
    print(f"❌ Пользователь {username} не найден на сервере")
    return None


async def process_queue():
    """Обрабатывает очередь проверок пользователей"""
    while True:
        print("Ожидание данных в очереди...")
        greeting = await queue.get()  # Получаем никнейм и приветствие из очереди
        print(f"📌приветствие: {greeting}")
        


async def send_verification_message(member):
    """Отправляет сообщение пользователю после успешной проверки"""
    try:
        view = LanguageSelectView()
        embed = discord.Embed(
            title="Please select your preferred language.",
            color=discord.Color.orange()
        )
        await member.send(embed=embed, view=view)
    except discord.Forbidden:
        print(f"❌ Не удалось отправить сообщение {member.name}, личные сообщения закрыты")


class LanguageSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()
        languages = [
            ("English", "🇬🇧"), ("French", "🇫🇷"), ("German", "🇩🇪"),
            ("Spanish", "🇪🇸"), ("Italian", "🇮🇹"), ("Polish", "🇵🇱"),
            ("Portuguese", "🇵🇹"), ("Russian", "🇷🇺"), ("Ukrainian", "🇺🇦"),
            ("Chinese", "🇨🇳")
        ]
        for lang, emoji in languages:
            self.add_item(LanguageButton(label=lang, emoji=emoji))
class LanguageButton(discord.ui.Button):
    def __init__(self, label, emoji):
        super().__init__(label=label, style=discord.ButtonStyle.primary, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        lang = self.label
        translation = translations[lang]
        try:
            await interaction.response.defer(ephemeral=True)
            # Отправить сообщение без ответа
            await interaction.user.send(embed=create_embed(translation["welcome"], discord.Color.orange()))
            
            # Запросить никнейм
            def check(m):
                return m.author == interaction.user and isinstance(m.channel, discord.DMChannel)

            msg = await bot.wait_for('message', check=check)
            username = msg.content

            # Отправить сообщение с выбором уровня
            view = LevelSelectView()
            embed = discord.Embed(
                title=translation['level'],
                color=discord.Color.orange()
            )
            await interaction.user.send(embed=embed, view=view)
            print("Сообщение с выбором уровня отправлено")

        except discord.Forbidden:
            await interaction.user.send(embed=create_embed(translations[lang]["enable_dm"], discord.Color.red()))

class LevelButton(discord.ui.Button):
    def __init__(self, label):
        super().__init__(label=label, style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        level = self.label
        translation = translations.get(interaction.locale, translations["English"])  # Используем английский по умолчанию, если перевод не найден
        try:
            # Обработка выбора уровня
            await interaction.response.defer(ephemeral=True)
            prepare_message = await interaction.user.send(embed=create_embed(translation["prepare_check"], discord.Color.orange()))

            # Проверка (пока пустышка, таймер на 3 секунды)
            await asyncio.sleep(3)
            await prepare_message.delete()

            # Отправить сообщение после задержки
            await interaction.user.send(embed=create_embed(translation["check_complete"], discord.Color.orange()))

            # Проверить, что значения не пустые
            verify_message = translation.get("verify", "").strip()
            verify_link_message = translation.get("verify_link", "").strip()

            if verify_message and verify_link_message:
                # Объединить два сообщения в одно
                await interaction.user.send(embed=create_embed_with_title(verify_message, verify_link_message, discord.Color.orange()))
            else:
                await interaction.user.send(embed=create_embed("❌ Error: Translation is missing.", discord.Color.red()))

        except discord.Forbidden:
            await interaction.user.send(embed=create_embed(translation["enable_dm"], discord.Color.red()))
            print("Не удалось отправить сообщение, личные сообщения закрыты")

class LevelSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()
        levels = range(1, 11)  # Уровни от 1 до 10
        for level in levels:
            self.add_item(LevelButton(label=str(level)))


def create_embed(message, color):
    return discord.Embed(description=message, color=color)

def create_embed_with_title(title, description, color):
    embed = discord.Embed(title=f"**{title}**", description=description, color=color)
    return embed

async def run_discord():
    await bot.start(DISCORD_TOKEN)

def create_embed(message, color):
    return discord.Embed(description=message, color=color)

def create_embed_with_title(title, description, color):
    embed = discord.Embed(title=f"**{title}**", description=description, color=color)
    return embed

async def run_discord():
    await bot.start(DISCORD_TOKEN)

