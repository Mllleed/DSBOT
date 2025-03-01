import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
from DSbot import send_verification_message, check_discord_user # Импортируем только нужную функцию

load_dotenv()
TOKEN = os.getenv("TG_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()
queue = asyncio.Queue()  # Очередь для передачи данных

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
    

    # Проверяем пользователя в Discord
    member = await check_discord_user(user_name)
    
    if member:
       await message.answer(f"Ваше имя сохранено: {user_name}")
       await send_verification_message(member)
    else:
        await message.answer("❌ Пользователь не найден на сервере Discord.")

    await state.clear()

async def start_telegram():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

# Запуск обоих ботов
async def main():
    from DSbot import run_discord  # Избегаем циклического импорта
    await asyncio.gather(
        start_telegram(),
        run_discord()
    )

if __name__ == "__main__":
    asyncio.run(main())

