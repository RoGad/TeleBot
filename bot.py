import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor

from io import open

def TeleBot():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token="6292399749:AAEL2xgOXJGC7NnFtUMu1xujM6upo8FxZ2M")
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    class Bolniza(StatesGroup):
        name = State()
        doctor = State()
        namePoisk = State()
        datetime = State()

    available_slots = {
        'Стоматолог': {
            'Пн': ['14:00 - 16:00'],
            'Вт': ['10:00 - 12:00', '14:00 - 16:00'],
            'Ср': ['16:00 - 18:00'],
            'Чт': ['10:00 - 12:00'],
            'Пт': ['14:00 - 16:00'],
            'Сб': ['10:00 - 12:00'],
            'Вс': ['16:00 - 18:00']
        },
        'Дерматолог': {
            'Пн': ['14:00 - 16:00'],
            'Вт': ['10:00 - 12:00', '14:00 - 16:00'],
            'Ср': ['16:00 - 18:00'],
            'Чт': ['10:00 - 12:00'],
            'Пт': ['14:00 - 16:00'],
            'Сб': ['10:00 - 12:00'],
            'Вс': ['16:00 - 18:00']
        },
        'Эпилептолог': {
            'Пн': ['14:00 - 16:00'],
            'Вт': ['10:00 - 12:00', '14:00 - 16:00'],
            'Ср': ['16:00 - 18:00'],
            'Чт': ['10:00 - 12:00'],
            'Пт': ['14:00 - 16:00'],
            'Сб': ['10:00 - 12:00'],
            'Вс': ['16:00 - 18:00']
        },
        'Терапевт': {
            'Пн': ['14:00 - 16:00'],
            'Вт': ['10:00 - 12:00', '14:00 - 16:00'],
            'Ср': ['16:00 - 18:00'],
            'Чт': ['10:00 - 12:00'],
            'Пт': ['14:00 - 16:00'],
            'Сб': ['10:00 - 12:00'],
            'Вс': ['16:00 - 18:00']
        }
    }

    @dp.message_handler(commands=['start'])
    async def start_command(message: types.Message):
        text = f'Привет, {message.chat.username}! Я бот, который записывает на прием к врачу.\n'
        global mainMenu
        mainMenu = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ['Записаться на прием', 'К кому я записан?']
        mainMenu.add(*buttons)
        await message.reply(text, reply_markup=mainMenu)

    @dp.message_handler(text=['Записаться на прием'])
    async def write(message: types.Message):
        text = 'Введите ваши ФИО'
        await message.reply(text, reply=False)
        await Bolniza.name.set()

    @dp.message_handler(state=Bolniza.name)
    async def process_name(message: types.Message, state: FSMContext):
        async with state.proxy() as zapis:
            zapis['name'] = message.text
        text = f"Хорошо, {message.text}. Осталось выбрать специалиста."
        buttons = ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton('Стоматолог'), KeyboardButton('Дерматолог'), KeyboardButton('Эпилептолог'), KeyboardButton('Терапевт'))
        await message.reply(text, reply_markup=buttons)
        await Bolniza.doctor.set()

    @dp.message_handler(text=['К кому я записан?'])
    async def start(message: types.Message):
        text = 'Введите ваши ФИО для поиска'
        await message.reply(text, reply=False)
        await Bolniza.namePoisk.set()

    @dp.message_handler(state=Bolniza.namePoisk)
    async def process_namePoisk(message: types.Message, state: FSMContext):
        async with state.proxy() as zapis:
            zapis['namePoisk'] = message.text
        with open('doctor.txt', 'r') as f:
            appointments = f.read()
            found_appointments = [line for line in appointments.split('\n') if zapis['namePoisk'] in line]
        if found_appointments:
            mes = f'Ваши записи на прием:\n\n'
            mes += '\n\n'.join(found_appointments)
        else:
            mes = 'Вы не записывались!'
        await message.reply(mes, reply=False)
        await state.finish()

    @dp.message_handler(state=Bolniza.doctor)
    async def process_distance(message: types.Message, state: FSMContext):
        async with state.proxy() as marathonData:
            marathonData['doctor'] = message.text
        text = f"Отлично, вы выбрали специалиста: {message.text}! Теперь выберите дату и время:"
        specialist_slots = available_slots.get(marathonData['distance'])
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        for day, slots in specialist_slots.items():
            buttons.add(KeyboardButton(f'{day}: {" - ".join(slots)}'))
        await message.reply(text, reply_markup=buttons)
        await Bolniza.datetime.set()

    @dp.message_handler(state=Bolniza.datetime)
    async def process_datetime(message: types.Message, state: FSMContext):
        async with state.proxy() as zapis:
            zapis['datetime'] = message.text
        text = "Спасибо! Я сохранил ваши данные. Вы записаны на прием по следующим параметрам:"
        text += f"\nФИО: {zapis['name']}"
        text += f"\nСпециалист: {zapis['distance']}"
        text += f"\nДата и время: {zapis['datetime']}"
        await message.reply(text, reply_markup=mainMenu)

        # Write data to the file
        with open('doctor.txt', 'a') as f:
            f.write(f"ФИО: {zapis['name']}\n")
            f.write(f"Специалист: {zapis['distance']}\n")
            f.write(f"Дата и время: {zapis['datetime']}\n\n")

        await state.finish()

    @dp.message_handler(commands=['get_data'])
    async def get_data_command(message: types.Message):
        with open('doctor.txt', 'r') as f:
            appointments = f.read()
        await message.reply(appointments)

    executor.start_polling(dp, skip_updates=True)
