from aiogram.dispatcher.filters.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_patronymic = State()
    waiting_for_class = State()
    waiting_for_shift = State()
    waiting_for_phone = State()

class ScheduleStates(StatesGroup):
    uploading_first_shift = State()
    uploading_second_shift = State()
    date_input = State()
    waiting_for_date = State()

class AnnouncementStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_media = State()
    confirm_announcement = State()
    uploading_first_shift = State()
    uploading_second_shift = State()
    waiting_for_date = State()