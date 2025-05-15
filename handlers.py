from aiogram import types
from keyboard_utils import get_main_keyboard
from announcement_handlers import process_announcement_command
from aiogram.dispatcher import FSMContext
from keyboard_utils import get_main_keyboard
from db_utils import register_user, get_user_profile

async def bot_info(message: types.Message):
    bot_info_text = (
        "🤖 *О боте*\n\n"
        "Этот бот поможет вам:\n"
        "📅 Просматривать расписание занятий\n"
        "📋 Получать важные новости и объявления\n"
        "Разработан для удобства учащихся и преподавателей.\n"
        "По вопросам и предложениям @airwar31."
    )
    await message.answer(
        bot_info_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(message.from_user.id)
    )


async def process_profile(message: types.Message):
    user = get_user_profile(message.from_user.id)
    if not user:
        await message.reply("Вы еще не зарегистрированы. Используйте /start для регистрации.")
        return
        
    profile_text = f"""👤 Профиль ученика:
Имя: {user['name']}
Фамилия: {user['surname']}
Отчество: {user['patronymic']}
Класс: {user['class']}
Смена: {user['shift']}
Телефон: {user['phone']}"""
    
    await message.reply(profile_text)

from registration_handlers import process_registration_step

async def process_name(message: types.Message, state: FSMContext):
    await process_registration_step(message, state, "name")

async def process_surname(message: types.Message, state: FSMContext):
    await process_registration_step(message, state, "surname")

async def process_patronymic(message: types.Message, state: FSMContext):
    await process_registration_step(message, state, "patronymic")

async def process_class(message: types.Message, state: FSMContext):
    await process_registration_step(message, state, "class")

async def process_shift(message: types.Message, state: FSMContext):
    await process_registration_step(message, state, "shift")

async def process_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
        user_data = {
            'name': data['name'],
            'surname': data['surname'],
            'patronymic': data['patronymic'],
            'class': data['class'],
            'shift': data['shift'],
            'phone': data['phone'],
            'username': message.from_user.username
        }
        register_user(message.from_user.id, user_data)
    
    await state.finish()
    await message.reply("Регистрация завершена!", reply_markup=get_main_keyboard(message.from_user.id))