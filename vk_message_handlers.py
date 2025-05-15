from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from vk_keyboards import get_vk_news_keyboard
from vk_handlers import get_vk_news, forward_vk_post_to_telegram
from vk_states import VKStates

async def process_vk_news(message: types.Message, state: FSMContext):
    await VKStates.viewing_news.set()
    posts = await get_vk_news()
    await state.update_data(posts=posts, page=0)
    await show_current_page(message.bot, message.from_user.id, state)

async def show_current_page(bot: Bot, user_id: int, state: FSMContext):
    data = await state.get_data()
    posts = data.get('posts', [])
    page = data.get('page', 0)
    
    if posts:
        current_post = posts[page]
        await forward_vk_post_to_telegram(bot, current_post, user_id)
        keyboard = get_vk_news_keyboard(has_prev=page > 0, has_next=page < len(posts)-1)
        last_message = await bot.send_message(user_id, "Используйте кнопки для навигации:", reply_markup=keyboard)
        await state.update_data(last_message_id=last_message.message_id)
async def process_vk_news_prev(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data.get('page', 0)
    if page > 0:
        await state.update_data(page=page-1)
        last_message_id = data.get('last_message_id')
        if last_message_id:
            try:
                await callback.bot.delete_message(callback.from_user.id, last_message_id)
            except:
                pass
        await show_current_page(callback.bot, callback.from_user.id, state)
    await callback.answer()

async def process_vk_news_next(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data.get('page', 0)
    posts = data.get('posts', [])
    if page < len(posts) - 1:
        await state.update_data(page=page+1)
        last_message_id = data.get('last_message_id')
        if last_message_id:
            try:
                await callback.bot.delete_message(callback.from_user.id, last_message_id)
            except:
                pass
        await show_current_page(callback.bot, callback.from_user.id, state)
    await callback.answer()

async def process_vk_news_exit(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get('last_message_id')
    if last_message_id:
        try:
            await callback.bot.delete_message(callback.from_user.id, last_message_id)
        except:
            pass
    await state.finish()
    await callback.answer()