import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Токен и ID сервера
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

# Устанавливаем интенты
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Префикс команд
bot = commands.Bot(command_prefix="!", intents=intents)

# Очередь для передачи данных между ботами
queue = asyncio.Queue()

MESSAGE_TEXT = '✅ Проверка пройдена, пользователь найден на сервере!'


@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} запущен и подключен к серверу!")
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f"👥 Число участников на сервере: {len(guild.members)}")
    else:
        print("❌ Бот не подключен к серверу или ID неверен")

@bot.command()
async def add(ctx, username: str):
    """Добавляет ник в очередь вручную"""
    await queue.put(username)
    await ctx.send(f"✅ {username} добавлен в очередь!")


async def check_discord_user(username):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("❌ Ошибка: Бот не находится на сервере с указанным ID")
        return None

    username_lower = username.lower()
    print(f"🔍 Ищу пользователя: {username}")

    for member in guild.members:
        print(f"👤 Проверяю: {member.name} ({member.display_name})")
        if member.name.lower() == username_lower or member.display_name.lower() == username_lower:
            print(f"✅ Найден: {member.name}")
            return member  # Возвращаем объект участника

    print(f"❌ Пользователь {username} не найден на сервере")
    return None


async def process_queue():
    """Обрабатывает очередь проверок пользователей"""
    while True:
        print("Ожидание данных в очереди...")
        username = await queue.get()  # Получаем никнейм из очереди
        print(f"📌 Получен никнейм: {username}")
        
        member = await check_discord_user(username)
        print(f"🔎 Проверка пользователя: {member}")

        if member:
            print(f"✅ Пользователь {username} найден, отправляю сообщение...")
            await send_verification_message(member)
        else:
            print(f"❌ Пользователь {username} не найден на сервере")

async def send_verification_message(member):
    """Отправляет сообщение пользователю после успешной проверки"""
    try:
        view = LanguageSelectView()
        embed = discord.Embed(
            title="Please select your preferred language.",
            color=discord.Color.orange()
        )
        await member.send(MESSAGE_TEXT)
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
        try:
            await interaction.user.send(f"✅ Вы выбрали язык: {self.label}")
            await interaction.response.send_message("📩 Я отправил сообщение в ЛС", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Не могу отправить сообщение в ЛС! Разрешите личные сообщения.", ephemeral=True)
        
        await asyncio.sleep(3)
        embed = discord.Embed(title='✅ Проверка завершена!', color=discord.Color.green())
        await interaction.user.send(embed=embed)


async def run_discord():
    await bot.start(DISCORD_TOKEN)

