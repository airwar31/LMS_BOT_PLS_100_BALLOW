from datetime import datetime, timedelta
from db_utils import get_db_connection
from aiogram import types
from notifications import send_schedule_notification
from schedule_db import save_schedule
from aiogram.dispatcher import FSMContext
from states import ScheduleStates
from keyboard_utils import get_main_keyboard, get_date_selection_keyboard
from config import ADMIN_ID
from schedule_keyboards import get_schedule_upload_keyboard
async def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

async def handle_admin_date(message: types.Message, state: FSMContext) -> bool:
    if not await validate_date(message.text):
        await message.reply("Неверный формат даты. Используйте формат ГГГГ-ММ-ДД (например, 2025-01-01)")
        return False
        
    async with state.proxy() as data:
        data['schedule_date'] = message.text
        
    return True


async def process_schedule_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("📅 Расписание на сегодня"),
        types.KeyboardButton("📅 Расписание на завтра")
    )
    keyboard.add(types.KeyboardButton("📅 Выбрать дату"))
    keyboard.add(types.KeyboardButton("🔙 Главное меню"))
    await message.answer("Выберите действие:", reply_markup=keyboard)

async def process_main_menu(message: types.Message):
    await message.answer("Главное меню", reply_markup=get_main_keyboard(message.from_user.id))

async def process_admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_ID:
        await message.answer("У вас нет доступа к панели администратора.")
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("📝 Загрузить расписание"), types.KeyboardButton("🎉 Управление событиями"))
    keyboard.add(types.KeyboardButton("📢 Сделать объявление"))
    keyboard.add(types.KeyboardButton("🔙 Главное меню"))
    await message.answer("Панель администратора", reply_markup=keyboard)

async def show_schedule(chat_id: int, date: str):
    from db_utils import get_user_profile
    conn = get_db_connection()
    try:
        user_profile = get_user_profile(chat_id)
        if not user_profile:
            return None, None
            
        user_shift = user_profile.get('shift')
        
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT first_shift_photo, second_shift_photo FROM schedule WHERE date = ?', (date,))
            result = cursor.fetchone()
            
            if not result:
                return None, None
                
            first_shift, second_shift = result
            if user_shift == '1':
                return first_shift, None
            elif user_shift == '2':
                return None, second_shift
            else:
                return None, None
    except Exception as e:
        print(f"Error getting schedule: {str(e)}")
        return None, None

async def process_schedule_view(message: types.Message, target_date: str = None, reply_markup = None):
    from schedule_db import get_schedule, delete_schedule
    if target_date is None:
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        first_shift, second_shift = await show_schedule(message.chat.id, target_date)
        if not first_shift and not second_shift:
            await message.answer("Расписание на указанную дату не найдено.", reply_markup=reply_markup)
            return

        try:
            if first_shift:
                await message.answer_photo(first_shift, caption="Расписание первой смены", reply_markup=reply_markup)
            if second_shift:
                await message.answer_photo(second_shift, caption="Расписание второй смены", reply_markup=reply_markup)
        except Exception as e:
            if "WrongFileIdentifier" in str(e):
                delete_schedule(target_date)
                await message.answer("Расписание устарело, требуется повторная загрузка.", reply_markup=reply_markup)
            else:
                print(f"Error sending photos: {str(e)}")
                await message.answer("Ошибка при отправке расписания.", reply_markup=reply_markup)

    except Exception as e:
        print(f"Error displaying schedule: {str(e)}")
        await message.answer("Произошла ошибка при отображении расписания", reply_markup=reply_markup)

async def process_schedule_today(message: types.Message):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        await process_schedule_view(message, today)
    except Exception as e:
        print(f"Error in process_schedule_today: {str(e)}")
        await message.answer("Произошла ошибка при получении расписания на сегодня")

async def process_schedule_tomorrow(message: types.Message):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    await process_schedule_view(message, tomorrow)

async def process_choose_date(message: types.Message):
    await ScheduleStates.waiting_for_date.set()
    await message.answer(
        "Введите дату в формате ГГГГ-ММ-ДД (например, 2024-01-25):",
        reply_markup=get_date_selection_keyboard()
    )

async def process_date_input(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.finish()
        await message.answer(
            "Выбор даты отменен.",
            reply_markup=get_main_keyboard(message.from_user.id)
        )
        return

    try:
        input_date = datetime.strptime(message.text, '%Y-%m-%d')
        formatted_date = input_date.strftime('%Y-%m-%d')
        await state.finish()
        await process_schedule_view(message, formatted_date, reply_markup=get_main_keyboard(message.from_user.id))
    except ValueError:
        await message.answer(
            "Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД (например, 2024-01-25):",
            reply_markup=get_date_selection_keyboard()
        )
    
    

async def process_upload_schedule(message: types.Message):
    if message.from_user.id not in ADMIN_ID:
        await message.answer("У вас нет доступа к этой функции.")
        return
    from schedule_keyboards import get_schedule_upload_keyboard
    await message.answer("Пожалуйста, отправьте фото расписания для первой смены.", reply_markup=get_schedule_upload_keyboard())
    await ScheduleStates.uploading_first_shift.set()

async def process_first_shift_photo(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить загрузку":
        await state.finish()
        await message.answer("Загрузка расписания отменена.", reply_markup=types.ReplyKeyboardRemove())
        return
        
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото.")
        return
    
    photo = message.photo[-1]
    async with state.proxy() as data:
        data['first_shift'] = photo.file_id
        await message.answer("Теперь отправьте фото расписания для второй смены.", reply_markup=get_schedule_upload_keyboard())
        await ScheduleStates.uploading_second_shift.set()

async def process_second_shift_photo(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить загрузку":
        await state.finish()
        await message.answer("Загрузка расписания отменена.", reply_markup=types.ReplyKeyboardRemove())
        return
        
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото.")
        return
    
    photo = message.photo[-1]
    async with state.proxy() as data:
        data['second_shift'] = photo.file_id
        await message.answer("На какую дату загружается расписание? Формат: ГГГГ-ММ-ДД", reply_markup=get_schedule_upload_keyboard())
        await ScheduleStates.date_input.set()

async def process_admin_date_input(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить загрузку":
        await state.finish()
        await message.answer("Загрузка расписания отменена.", reply_markup=types.ReplyKeyboardRemove())
        return

    try:
        date = message.text
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            await message.answer("Неверный формат даты. Используйте формат ГГГГ-ММ-ДД", reply_markup=get_schedule_upload_keyboard())
            return

        async with state.proxy() as data:
            print(f"Processing date {date} with data: {data}")
            is_update = save_schedule(date, data['first_shift'], data['second_shift'])
            await message.answer(f"Расписание на {date} успешно загружено!", reply_markup=get_main_keyboard(message.from_user.id))
            bot = message.bot
            await send_schedule_notification(bot, date, is_update)
    except Exception as e:
        print(f"Error in process_admin_date_input: {str(e)}")
        async with state.proxy() as data:
            print(f"State data: {data}")
        await message.answer(f"Произошла ошибка при сохранении расписания: {str(e)}")
    finally:
        await state.finish()