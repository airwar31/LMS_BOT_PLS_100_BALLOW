from aiogram import types
from states import RegistrationStates
from keyboard_utils import get_main_keyboard
import logging
from db_utils import get_user_profile

async def cmd_start(message: types.Message):
    try:
        user = get_user_profile(message.from_user.id)

        keyboard = get_main_keyboard(message.from_user.id)
        if user:
            await message.answer(f"С возвращением!\nГлавное меню:", reply_markup=keyboard)
        else:
            await message.answer("Добро пожаловать! Для начала давайте зарегистрируемся.\nВведите ваше имя:", reply_markup=types.ReplyKeyboardRemove())
            await RegistrationStates.waiting_for_name.set()
            
    except Exception as e:
        logging.error(f"Database error in cmd_start: {e}")
        await message.reply("Произошла ошибка при работе с базой данных. Попробуйте позже.")
        return