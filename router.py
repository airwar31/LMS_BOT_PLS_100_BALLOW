from aiogram import Dispatcher
from aiogram.filters import Text
from vk_message_handlers import process_vk_news, process_vk_news_prev, process_vk_news_next, process_vk_news_exit
from states import RegistrationStates, ScheduleStates, AnnouncementStates
from event_states import EventStates
from vk_states import VKStates
from event_handlers import (
    process_events_menu,
    process_current_events,
    process_admin_events,
    process_create_event,
    process_event_name,
    process_event_description,
    process_event_start_date,
    process_event_end_date,
    process_event_start_time,
    process_event_end_time,
    process_delete_event_request,
    process_delete_event
)
from command_handlers import cmd_start
from registration_handlers import start_registration, process_registration_step
from handlers import process_profile
from schedule_handlers import (
    process_schedule_today,
    process_schedule_tomorrow,
    process_schedule_menu,
    process_main_menu,
    process_admin_panel,
    process_choose_date,
    process_date_input,
    process_upload_schedule,
    process_first_shift_photo,
    process_second_shift_photo,
    process_admin_date_input
)
from announcement_handlers import (
    process_announcement_command,
    process_announcement_text,
    process_announcement_cancel,
    process_announcement_media,
    process_announcement_confirmation,
)
import handlers
from vk_message_handlers import (
    process_vk_news,
    process_vk_news_prev,
    process_vk_news_next,
    process_vk_news_exit
)

def register_handlers(dp: Dispatcher):
    from diary_handlers import (
    start_diary_auth,
    process_login,
    show_homework,
    show_grades,
    return_to_main_menu
)
    from diary_states import DiaryStates
    dp.register_message_handler(start_diary_auth, lambda msg: msg.text == "ЦОП", state="*")

    dp.register_message_handler(process_vk_news, commands=["vk_news"], state=None)
    dp.register_message_handler(process_vk_news, text="📰 VK Новости", state=None)
    dp.register_callback_query_handler(process_vk_news_prev, lambda c: c.data == "vk_news_prev", state=VKStates.viewing_news)
    dp.register_callback_query_handler(process_vk_news_next, lambda c: c.data == "vk_news_next", state=VKStates.viewing_news)
    dp.register_callback_query_handler(process_vk_news_exit, lambda c: c.data == "vk_news_exit", state=VKStates.viewing_news)

    dp.register_message_handler(process_announcement_cancel, lambda message: message.text == "❌ Отменить", 
                          state=[AnnouncementStates.waiting_for_text, AnnouncementStates.waiting_for_media, AnnouncementStates.confirm_announcement])
    dp.register_message_handler(process_announcement_text, state=AnnouncementStates.waiting_for_text)
    dp.register_message_handler(process_announcement_media, content_types=['text', 'photo', 'video'], state=AnnouncementStates.waiting_for_media)
    dp.register_message_handler(process_announcement_confirmation, state=AnnouncementStates.confirm_announcement)

    dp.register_message_handler(process_admin_panel, text="⚙️ Панель администратора", state="*")
    dp.register_message_handler(process_upload_schedule, text="📝 Загрузить расписание", state="*")
    dp.register_message_handler(process_admin_events, text="🎉 Управление событиями", state="*")
    dp.register_message_handler(process_announcement_command, text="📢 Сделать объявление", state="*")

    dp.register_message_handler(process_events_menu, text="📋 Новости")
    dp.register_message_handler(process_current_events, text="🎉 Мероприятия")
    dp.register_message_handler(handlers.bot_info, text="ℹ️ Информация")
    dp.register_message_handler(process_admin_events, text="🎉 Управление событиями")
    dp.register_message_handler(process_create_event, text="➕ Создать событие")
    dp.register_message_handler(process_delete_event_request, text="❌ Удалить событие")
    dp.register_message_handler(process_delete_event, state=EventStates.waiting_for_event_id)
    dp.register_message_handler(process_main_menu, text=["🔙 Главное меню", "🔙 Назад"])
    
    dp.register_message_handler(process_event_name, state=EventStates.waiting_for_name)
    dp.register_message_handler(process_event_description, state=EventStates.waiting_for_description)
    dp.register_message_handler(process_event_start_date, state=EventStates.waiting_for_start_date)
    dp.register_message_handler(process_event_end_date, state=EventStates.waiting_for_end_date)
    dp.register_message_handler(process_event_start_time, state=EventStates.waiting_for_start_time)
    dp.register_message_handler(process_event_end_time, state=EventStates.waiting_for_end_time)
    
    dp.register_message_handler(cmd_start, commands=['start'])
    
    dp.register_message_handler(start_registration, commands=['register'])
    dp.register_message_handler(lambda message: process_registration_step(message, dp.current_state(), field='cancel'), text="❌ Отменить регистрацию", state=RegistrationStates.all_states)
    dp.register_message_handler(process_profile, lambda message: message.text == "👤 Профиль")
    dp.register_message_handler(lambda message: process_registration_step(message, dp.current_state(), field='name'), state=RegistrationStates.waiting_for_name)
    dp.register_message_handler(lambda message: process_registration_step(message, dp.current_state(), field='surname'), state=RegistrationStates.waiting_for_surname)
    dp.register_message_handler(lambda message: process_registration_step(message, dp.current_state(), field='patronymic'), state=RegistrationStates.waiting_for_patronymic)
    dp.register_message_handler(lambda message: process_registration_step(message, dp.current_state(), field='class'), state=RegistrationStates.waiting_for_class)
    dp.register_message_handler(lambda message: process_registration_step(message, dp.current_state(), field='shift'), state=RegistrationStates.waiting_for_shift)
    dp.register_message_handler(lambda message: process_registration_step(message, dp.current_state(), field='phone'), state=RegistrationStates.waiting_for_phone)

    dp.register_message_handler(process_schedule_menu, lambda message: message.text == "📅 Расписание")
    dp.register_message_handler(process_main_menu, lambda message: message.text == "🔙 Главное меню")
    dp.register_message_handler(process_admin_panel, lambda message: message.text == "⚙️ Панель администратора")
    dp.register_message_handler(process_schedule_today, lambda message: message.text == "📅 Расписание на сегодня")
    dp.register_message_handler(process_schedule_tomorrow, lambda message: message.text == "📅 Расписание на завтра")
    dp.register_message_handler(process_choose_date, lambda message: message.text == "📅 Выбрать дату")
    dp.register_message_handler(process_date_input, state=ScheduleStates.waiting_for_date)
    dp.register_message_handler(process_upload_schedule, lambda message: message.text == "📝 Загрузить расписание")
    dp.register_message_handler(process_first_shift_photo, content_types=['photo'], state=ScheduleStates.uploading_first_shift)
    dp.register_message_handler(process_second_shift_photo, content_types=['photo'], state=ScheduleStates.uploading_second_shift)
    dp.register_message_handler(process_admin_date_input, state=ScheduleStates.date_input)