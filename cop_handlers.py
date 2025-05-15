from aiogram import types

async def open_cop_mini_app(message: types.Message):
    await message.answer(
        "Нажмите кнопку ниже, чтобы открыть приложение COP:",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(
                text="Открыть COP",
                web_app=types.WebAppInfo(url="https://cop.admhmao.ru")
            )
        )
    )