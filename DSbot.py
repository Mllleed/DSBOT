import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from languages import translations
from database import log_action

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

@bot.event
async def on_member_join(member):
    log_action(member.id, member.name, 'joined the server')
    await member.send("Welcome to the server!")

@bot.event
async def on_member_remove(member):
    log_action(member.id, member.name, 'left the server')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    log_action(message.author.id, message.author.name, 'sent a message')
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    log_action(after.author.id, after.author.name, f'edited a message from "{before.content}" to "{after.content}"')

@bot.event
async def on_message_delete(message):
    log_action(message.author.id, message.author.name, f'deleted a message: "{message.content}"')

@bot.event
async def on_reaction_add(reaction, user):
    log_action(user.id, user.name, f'added reaction {reaction.emoji} to message: "{reaction.message.content}"')

@bot.event
async def on_reaction_remove(reaction, user):
    log_action(user.id, user.name, f'removed reaction {reaction.emoji} from message: "{reaction.message.content}"')

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        log_action(member.id, member.name, f'joined voice channel: {after.channel.name}')
    elif before.channel is not None and after.channel is None:
        log_action(member.id, member.name, f'left voice channel: {before.channel.name}')
    elif before.channel != after.channel:
        log_action(member.id, member.name, f'switched voice channel from {before.channel.name} to {after.channel.name}')

@bot.event
async def on_member_update(before, after):
    log_action(after.id, after.name, 'updated profile')

@bot.event
async def on_user_update(before, after):
    log_action(after.id, after.name, 'updated user profile')

@bot.event
async def on_guild_update(before, after):
    log_action(bot.user.id, bot.user.name, 'updated guild settings')

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
            # Ответить взаимодействием, чтобы не было ошибки
            await interaction.response.send_message(embed=create_embed(translation["welcome"], discord.Color.orange()), ephemeral=True)

            # Запросить никнейм
            def check(m):
                return m.author == interaction.user and isinstance(m.channel, discord.DMChannel)

            msg = await bot.wait_for('message', check=check)
            username = msg.content

            # Проверка (пока пустышка, таймер на 3 секунды)
            await asyncio.sleep(3)
            
            # Проверить, что значения не пустые
            verify_message = translation.get("verify", "").strip()
            verify_link_message = translation.get("verify_link", "").strip()
            
            if verify_message and verify_link_message:
                # Объединить два сообщения в одно
                await interaction.user.send(embed=create_embed_with_title(verify_message, verify_link_message, discord.Color.orange()))
            else:
                await interaction.user.send(embed=create_embed("❌ Error: Translation is missing.", discord.Color.red()))

        except discord.Forbidden:
            await interaction.response.send_message(embed=create_embed(translations[lang]["enable_dm"], discord.Color.red()), ephemeral=True)

def create_embed(message, color):
    return discord.Embed(description=message, color=color)

def create_embed_with_title(title, description, color):
    embed = discord.Embed(title=f"**{title}**", description=description, color=color)
    return embed

async def run_discord():
    await bot.start(DISCORD_TOKEN)

