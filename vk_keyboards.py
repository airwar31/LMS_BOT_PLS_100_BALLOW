from aiogram import types

def get_vk_news_keyboard(has_prev=False, has_next=False):
    keyboard = types.InlineKeyboardMarkup()
    row = []
    if has_prev:
        row.append(types.InlineKeyboardButton(text="◀️ Назад", callback_data="vk_news_prev"))
    if has_next:
        row.append(types.InlineKeyboardButton(text="Вперед ▶️", callback_data="vk_news_next"))
    if row:
        keyboard.row(*row)
    keyboard.add(types.InlineKeyboardButton(text="❌ Закрыть", callback_data="vk_news_exit"))
    return keyboard