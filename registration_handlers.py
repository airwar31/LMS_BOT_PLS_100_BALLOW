from aiogram import types
from aiogram.dispatcher import FSMContext
from states import RegistrationStates
from db_utils import register_user
from keyboard_utils import get_registration_keyboard, get_main_keyboard

REGISTRATION_STEPS = {
    'name': {
        'prompt': "Введите вашу фамилию:",
        'next_state': RegistrationStates.waiting_for_surname
    },
    'surname': {
        'prompt': "Введите ваше отчество:",
        'next_state': RegistrationStates.waiting_for_patronymic
    },
    'patronymic': {
        'prompt': "Введите ваш класс (например, '10А'):",
        'next_state': RegistrationStates.waiting_for_class
    },
    'class': {
        'prompt': "Введите вашу смену (1 или 2):",
        'next_state': RegistrationStates.waiting_for_shift
    },
    'shift': {
        'prompt': "Введите ваш номер телефона:",
        'next_state': RegistrationStates.waiting_for_phone,
        'validator': lambda x: x in ['1', '2'],
        'error_message': "Пожалуйста, введите 1 или 2:"
    },
    'phone': {
        'prompt': "Регистрация завершена! Теперь вы можете пользоваться всеми функциями бота.",
        'next_state': None,
        'final_step': True
    }
}

async def start_registration(message: types.Message):
    await RegistrationStates.waiting_for_name.set()
    keyboard = get_registration_keyboard()
    await message.reply("Введите ваше имя:", reply_markup=keyboard)

async def cancel_registration(message: types.Message, state: FSMContext):
    await state.finish()
    await start_registration(message)

async def process_registration_step(message: types.Message, state: FSMContext, field: str):
    if message.text == "❌ Отменить регистрацию":
        await cancel_registration(message, state)
        return

    step_config = REGISTRATION_STEPS.get(field)
    if not step_config:
        return
    if 'validator' in step_config and not step_config['validator'](message.text):
        await message.reply(step_config['error_message'])
        return
    
    async with state.proxy() as data:
        data[field] = message.text
        
    if step_config.get('final_step'):
        user_data = dict(data)
        register_user(
            user_id=message.from_user.id,
            name=user_data['name'],
            surname=user_data['surname'],
            patronymic=user_data['patronymic'],
            class_name=user_data['class'],
            shift=user_data['shift'],
            phone=user_data['phone'],
            telegram_username=message.from_user.username
        )
        await state.finish()
    else:
        await step_config['next_state'].set()
        keyboard = get_registration_keyboard()
        await message.reply(step_config['prompt'], reply_markup=keyboard)
    
    if step_config.get('final_step'):
        keyboard = get_main_keyboard(message.from_user.id)
        await message.reply(step_config['prompt'], reply_markup=keyboard)

