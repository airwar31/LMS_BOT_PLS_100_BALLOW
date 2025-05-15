from aiogram import types

def get_schedule_upload_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("❌ Отменить загрузку"))
    return keyboard