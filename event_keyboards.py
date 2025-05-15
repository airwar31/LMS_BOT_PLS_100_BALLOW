from aiogram import types

def get_event_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("🎉 Мероприятия"), types.KeyboardButton("📰 VK Новости"))
    keyboard.add(types.KeyboardButton("🔙 Главное меню"))
    return keyboard

def get_admin_event_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("➕ Создать событие"))
    keyboard.add(types.KeyboardButton("❌ Удалить событие"))
    keyboard.add(types.KeyboardButton("🔙 Назад"))
    return keyboard

def get_cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("❌ Отменить создание"))
    return keyboard