from aiogram.dispatcher.filters.state import State, StatesGroup

class EventStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_event_id = State()
    waiting_for_start_date = State()
    waiting_for_end_date = State()
    waiting_for_start_time = State()
    waiting_for_end_time = State()