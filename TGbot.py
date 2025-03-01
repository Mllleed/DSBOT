import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
from DSbot import send_verification_message, check_discord_user, queue  # Импортируем только нужную функцию
from database import check_bot_existence, session, User, LinkedUser

load_dotenv()
TOKEN = os.getenv("TG_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

list_names = ('CS2 EUROPE', )

class UserState(StatesGroup):
    waiting_for_name = State()
    waiting_for_greetings = State()

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
    await state.update_data(tg_id=callback.from_user.id)
    await state.set_state(UserState.waiting_for_name)

@dp.message(UserState.waiting_for_name)
async def receive_name(message: types.Message, state: FSMContext):
    user_name = message.text.strip()

    # Проверяем пользователя в Discord
    member = await check_discord_user(user_name)  # ← Ошибка! Ты забыл объявить member

    if member:
        await state.update_data(linked_users=user_name)  # ← Сначала сохраняем в state
        await message.answer(
            "Выберите никнейм, от кого приветствовать.", 
            reply_markup=create_greeting_keyboard()
        )
        await state.set_state(UserState.waiting_for_greetings)
    else:
        await message.answer("❌ Пользователь не найден на сервере Discord.")
        await state.clear()

@dp.callback_query(F.data.startswith('greet_'))
async def get_greetings(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state != UserState.waiting_for_greetings.state:
        return
    
    selected_greeting = callback.data.replace('greet_', "")
    await callback.message.answer(f"Приветствие выбрано: {selected_greeting.replace('_', ' ').title()}")

    data = await state.get_data()
    user_name = data.get('linked_users')
    member = await check_discord_user(user_name)
    if member:
        await send_verification_message(member)

#   tg_id = data['tg_id']
#   linked_users = data['linked_users']

    # Добавляем данные в базу данных
#    new_linked_user = LinkedUser(discord_name=linked_users)
#    session.add(new_linked_user)
#    session.commit()

    # Получаем id новосозданной записи
#   linked_users_id = new_linked_user.id

    # Добавляем данные в таблицу users
#   new_user = User(tg_id=tg_id, greetings=selected_greeting, linked_users_id=linked_users_id)
#    session.add(new_user)
#    session.commit()
    await queue.put(selected_greeting)
    # Очистить состояние
    await state.clear()

def create_greeting_keyboard():
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"greet_{name.lower()}")]
        for name in list_names
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Функция для запуска Telegram бота
async def start_telegram():
    await dp.start_polling(bot)

# Запуск обоих ботов
async def main():
    from DSbot import run_discord  # Избегаем циклического импорта
    await asyncio.gather(
        start_telegram(),
        run_discord()
    )

if __name__ == "__main__":
    check_bot_existence()
    asyncio.run(main())

