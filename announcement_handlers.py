from aiogram import types
from aiogram.dispatcher import FSMContext
from states import AnnouncementStates
from notifications import send_announcement
from keyboard_utils import get_main_keyboard, get_announcement_keyboard, get_confirmation_keyboard
async def process_announcement_command(message: types.Message):
    await message.reply("Введите текст объявления:", reply_markup=get_announcement_keyboard())
    
    await AnnouncementStates.waiting_for_text.set()

async def process_announcement_cancel(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.finish()
        await message.reply("Отправка объявления отменена.", reply_markup=get_main_keyboard(message.from_user.id))

async def process_announcement_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await process_announcement_cancel(message, state)
        return
    
    async with state.proxy() as data:
        data['announcement_text'] = message.text
    
    await message.reply("Теперь вы можете прикрепить фото или видео к объявлению (или нажмите 'Пропустить'):", 
                       reply_markup=get_announcement_keyboard(include_skip=True))
    await AnnouncementStates.waiting_for_media.set()

async def process_announcement_media(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await process_announcement_cancel(message, state)
        return
    
    async with state.proxy() as data:
        if message.text and message.text == "⏩ Пропустить":
            data['media'] = None
        else:
            if message.photo:
                data['media'] = {'type': 'photo', 'file_id': message.photo[-1].file_id}
            elif message.video:
                data['media'] = {'type': 'video', 'file_id': message.video.file_id}
            else:
                await message.reply("Пожалуйста, отправьте фото или видео, или нажмите 'Пропустить'")
                return
        
        preview = f"Предварительный просмотр объявления:\n\n{data['announcement_text']}"
        if data['media']:
            preview += "\n[Прикреплено медиа]"
        
        await message.reply(preview, reply_markup=get_confirmation_keyboard())
        await AnnouncementStates.confirm_announcement.set()

async def process_announcement_confirmation(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await process_announcement_cancel(message, state)
        return
    
    if message.text == "✅ Подтвердить":
        async with state.proxy() as data:
            await send_announcement(message.bot, data['announcement_text'], data.get('media'))
        await message.reply("Объявление отправлено всем пользователям!", 
                          reply_markup=get_main_keyboard(message.from_user.id))
        await state.finish()

