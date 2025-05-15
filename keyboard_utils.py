from aiogram import types
from config import ADMIN_ID

def get_registration_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("❌ Отменить регистрацию"))
    return keyboard

def get_date_selection_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("❌ Отменить"))
    return keyboard

def get_announcement_keyboard(include_skip=False):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if include_skip:
        keyboard.add(types.KeyboardButton("⏩ Пропустить"))
    keyboard.add(types.KeyboardButton("❌ Отменить"))
    return keyboard

def get_confirmation_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("✅ Подтвердить"))
    keyboard.add(types.KeyboardButton("❌ Отменить"))
    return keyboard

def get_main_keyboard(user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("🏢 COP"))
    keyboard.add(types.KeyboardButton("📅 Расписание"), types.KeyboardButton("📋 Новости"))
    keyboard.add(types.KeyboardButton("👤 Профиль"))
    keyboard.add(types.KeyboardButton("ℹ️ Информация"))
    if user_id in ADMIN_ID:
        keyboard.add(types.KeyboardButton("⚙️ Панель администратора"))
    return keyboard

def create_keyboard(buttons, row_width=2):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(buttons), row_width):
        row_buttons = buttons[i:i + row_width]
        keyboard.add(*[types.KeyboardButton(btn) for btn in row_buttons])
    return keyboard