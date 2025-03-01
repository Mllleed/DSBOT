import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TG_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()
queue = asyncio.Queue()

class UserState(StatesGroup):
    waiting_for_name = State()

keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Ввести имя', callback_data='enter_name')],
        [InlineKeyboardButton(text='Логи (не работает)', callback_data='log')],
    ]
)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.callback_query(F.data == "enter_name")
async def ask_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите никнейм:")
    await state.set_state(UserState.waiting_for_name)

@dp.message(UserState.waiting_for_name)
async def receive_name(message: types.Message, state: FSMContext):
    user_name = message.text.strip()

    await message.answer(f"Ваше имя сохранено: {user_name}")
    await queue.put((message.chat.id, user_name))  # Добавляем в очередь
    await process_queue()  # Запускаем обработку очереди
    await state.clear()


async def check_discord_user(username):
    from DSbot import check_discord_user, process_queue
    if await check_discord_user(member):
        await process_queue()


@dp.callback_query(F.data == "log")
async def logs_handler(callback: types.CallbackQuery):
    await callback.answer("Эта функция пока не работает 🚧", show_alert=True)


async def start_telegram():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

