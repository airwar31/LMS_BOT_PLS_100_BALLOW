from aiogram import types
from event_db import save_event, get_current_events
from aiogram.dispatcher import FSMContext
from datetime import datetime
import sqlite3
import logging
from notifications import send_announcement
from event_states import EventStates
from event_keyboards import get_event_keyboard, get_admin_event_keyboard, get_cancel_keyboard
from config import DATABASE
from event_db import delete_event, get_event
conn = sqlite3.connect(DATABASE)

async def process_events_menu(message: types.Message):
    keyboard = get_event_keyboard()
    await message.answer("🎉 Меню новостей:", reply_markup=keyboard)

async def process_current_events(message: types.Message):
    try:
        events = get_current_events()
        if not events:
            await message.answer("На данный момент нет активных событий на этой неделе.")
            return
    except Exception as e:
        logging.error(f"Error getting current events: {e}")
        await message.answer("Произошла ошибка при получении событий. Пожалуйста, попробуйте позже.")
        return
    
    response = "📋 Текущие события:\n\n"
    for event in events:
        start_date = datetime.strptime(event[3], '%Y-%m-%d').strftime('%d.%m.%Y')
        end_date = datetime.strptime(event[4], '%Y-%m-%d').strftime('%d.%m.%Y')
        response += f"📅 {event[1]}\n"
        response += f"📝 Описание: {event[2]}\n"
        response += f"📍 Когда: {start_date} - {end_date}\n"
        response += f"🕒 Время: {event[5]} - {event[6]}\n\n"
    
    await message.answer(response)

async def process_admin_events(message: types.Message):
    keyboard = get_admin_event_keyboard()
    await message.answer("⚙️ Управление событиями:", reply_markup=keyboard)

async def process_delete_event_request(message: types.Message):
    events = get_current_events()
    if not events:
        await message.answer("Нет доступных событий для удаления.")
        return
    
    events_list = "\n".join([f"ID: {event[0]} - {event[1]}" for event in events])
    await message.answer(f"Введите ID события для удаления:\n\n{events_list}")
    await EventStates.waiting_for_event_id.set()

async def process_delete_event(message: types.Message, state: FSMContext):
    try:
        event_id = int(message.text)
        event = get_event(event_id)
        if not event:
            await message.answer("Событие с указанным ID не найдено.")
            await state.finish()
            return
        
        delete_event(event_id)
        await message.answer(f"Событие '{event[1]}' успешно удалено.")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID события.")
    finally:
        await state.finish()

async def process_create_event(message: types.Message):
    await EventStates.waiting_for_name.set()
    await message.answer("Введите название мероприятия:", reply_markup=get_cancel_keyboard())

async def process_event_name(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить создание":
        await state.finish()
        await message.answer("Создание мероприятия отменено.", reply_markup=get_event_keyboard())
        return
    async with state.proxy() as data:
        data['name'] = message.text
    await EventStates.waiting_for_description.set()
    await message.answer("Введите описание мероприятия:", reply_markup=get_cancel_keyboard())

async def process_event_description(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить создание":
        await state.finish()
        await message.answer("Создание мероприятия отменено.", reply_markup=get_event_keyboard())
        return
    async with state.proxy() as data:
        data['description'] = message.text
    await EventStates.waiting_for_start_date.set()
    await message.answer("Введите дату начала мероприятия (в формате ДД.ММ.ГГГГ):", reply_markup=get_cancel_keyboard())

async def process_event_start_date(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить создание":
        await state.finish()
        await message.answer("Создание мероприятия отменено.", reply_markup=get_event_keyboard())
        return
    is_valid, normalized_date = await validate_date(message.text)
    if not is_valid:
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ")
        return
    
    async with state.proxy() as data:
        data['start_date'] = normalized_date
    await EventStates.waiting_for_end_date.set()
    await message.answer("Введите дату окончания мероприятия (в формате ДД.ММ.ГГГГ):", reply_markup=get_cancel_keyboard())

async def process_event_end_date(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить создание":
        await state.finish()
        await message.answer("Создание мероприятия отменено.", reply_markup=get_event_keyboard())
        return
    is_valid, normalized_date = await validate_date(message.text)
    if not is_valid:
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ")
        return
    
    async with state.proxy() as data:
        data['end_date'] = normalized_date
    await EventStates.waiting_for_start_time.set()
    await message.answer("Введите время начала мероприятия (в формате ЧЧ:ММ):", reply_markup=get_cancel_keyboard())

async def process_event_start_time(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить создание":
        await state.finish()
        await message.answer("Создание мероприятия отменено.", reply_markup=get_event_keyboard())
        return
    is_valid, normalized_time = await validate_time(message.text)
    if not is_valid:
        await message.answer("Неверный формат времени. Пожалуйста, используйте формат ЧЧ:ММ")
        return
    
    async with state.proxy() as data:
        data['start_time'] = normalized_time
    await EventStates.waiting_for_end_time.set()
    await message.answer("Введите время окончания мероприятия (в формате ЧЧ:ММ):", reply_markup=get_cancel_keyboard())

async def process_event_end_time(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить создание":
        await state.finish()
        await message.answer("Создание мероприятия отменено.", reply_markup=get_event_keyboard())
        return
    is_valid, normalized_time = await validate_time(message.text)
    if not is_valid:
        await message.answer("Неверный формат времени. Пожалуйста, используйте формат ЧЧ:ММ")
        return
    
    async with state.proxy() as data:
        data['end_time'] = normalized_time
        try:
            start_dt = datetime.strptime(f"{data['start_date']} {data['start_time']}", '%Y-%m-%d %H:%M')
            end_dt = datetime.strptime(f"{data['end_date']} {normalized_time}", '%Y-%m-%d %H:%M')
            if end_dt <= start_dt:
                await message.answer("Время окончания должно быть позже времени начала события")
                return
        except ValueError:
            await message.answer("Ошибка в формате даты/времени")
            return
        save_event(
            data['name'],
            data['description'],
            data['start_date'],
            data['end_date'],
            data['start_time'],
            data['end_time']
        )
        
        notification_text = f"🎉 Новое мероприятие!\n\n" \
                          f"📌 {data['name']}\n" \
                          f"📝 {data['description']}\n" \
                          f"📅 {data['start_date']} - {data['end_date']}\n" \
                          f"⏰ {data['start_time']} - {data['end_time']}"
        
        await send_announcement(message.bot, notification_text)
    
    await state.finish()
    await message.answer("Мероприятие успешно создано!")
    await message.answer("🎉 Меню новостей:", reply_markup=get_admin_event_keyboard())

async def validate_date(date_str: str) -> tuple[bool, str]:
    try:
        date_obj = datetime.strptime(date_str, '%d.%m.%Y')
        normalized_date = date_obj.strftime('%Y-%m-%d')
        return True, normalized_date
    except ValueError:
        return False, ''

async def validate_time(time_str: str) -> tuple[bool, str]:
    try:
        time_obj = datetime.strptime(time_str, '%H:%M')
        normalized_time = time_obj.strftime('%H:%M')
        return True, normalized_time
    except ValueError:
        return False, ''