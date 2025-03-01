import discord 
from config import settings
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

MESSAGE_TEXT = 'Проверка пройдена, пользователь участник сервера'

bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)

class LanguageSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()

        languages = [
                 ("English", "🇬🇧"), ("French", "🇫🇷"), ("German", "🇩🇪"), 
            ("Spanish", "🇪🇸"), ("Italian", "🇮🇹"), ("Polish", "🇵🇱"), 
            ("Portuguese", "🇵🇹"), ("Russian", "🇷🇺"), ("Ukrainian", "🇺🇦"), ("Chinese"                                                                              , "🇨🇳")
            ]

        for lang, emoji in languages:
            self.add_item(LanguageButton(label=lang, emoji=emoji))

class LanguageButton(discord.ui.Button):
    def __init__(self, label, emoji):
        super().__init__(label=label, style=discord.ButtonStyle.primary, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.user.send(f"Вы выбрали язык: {self.label}")
            await interaction.response.send_message("Я отправил сообщение в ЛС", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Не могу отправить вам сообщение в ЛС! Разрешите                                        личные сообщения.", ephemeral=True)
            return

        await asyncio.sleep(3)

        embed = discord.Embed(
                title='✅ Проверка завершена!',
                color=discord.Color.green()
            )
        await interaction.user.send(embed=embed)

class MessageWithButton(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(discord.ui.Button(label="Подробнее", url="https://www.google.com/"))

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен")

@bot.command()
async def language(ctx):
    """Команда для отправки сообщения с кнопкам выбора языка"""

    embed = discord.Embed(
            title="Please select your preferred language.",
            color=discord.Color.orange()
        )

    view = LanguageSelectView()
    
    try:
        await ctx.author.send(embed=embed, view=view)
        await ctx.send("Я отправил вам сообщения в ЛС", ephemeral=True)
    except discord.Forbidden:
        await ctx.send("Не могу отправить сообщения в ЛС! Разрешите личные сообщения")
@bot.command()
async def sendmsg(ctx, user: discord.Member):
    """Отправляет сообщение указанному пользователю, если он есть на сервере"""

    try:
        view = MessageWithButton()
        if user in ctx.guild.members:
           await user.send(MESSAGE_TEXT, view=view)
           await ctx.send(f"Этот пользователь не состоит на сервере!")
        else:
            await ctx.send('Этот пользователь не состоит на сервере')
    except discord.Forbidden:
        await ctx.send('Не удалось отправить сообщение. Возможно у пользователя закрыты л                                                                       ичные сообщения')
    except Exception as e:
        await ctx.send(f"Произошла ошибка: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
