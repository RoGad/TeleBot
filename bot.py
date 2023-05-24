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

    class Marathon(StatesGroup):
        name = State()
        distance = State()
        namePoisk = State()
        datetime = State()

    available_slots = {
        'Пн': ['14:00 - 16:00'],
        'Вт': ['10:00 - 12:00', '14:00 - 16:00'],
        'Ср': ['16:00 - 18:00'],
        'Чт': ['10:00 - 12:00'],
        'Пт': ['14:00 - 16:00'],
        'Сб': ['10:00 - 12:00'],
        'Вс': ['16:00 - 18:00']
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
        await Marathon.name.set()

    @dp.message_handler(state=Marathon.name)
    async def process_name(message: types.Message, state: FSMContext):
        async with state.proxy() as marathonData:
            marathonData['name'] = message.text
        text = f"Хорошо, {message.text}. Осталось выбрать специалиста."
        buttons = ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton('Стоматолог'), KeyboardButton('Дерматолог'), KeyboardButton('Эпилептолог'), KeyboardButton('Терапевт'))
        await message.reply(text, reply_markup=buttons)
        await Marathon.distance.set()

    @dp.message_handler(text=['К кому я записан?'])
    async def start(message: types.Message):
        text = 'Введите ваши ФИО для поиска'
        await message.reply(text, reply=False)
        await Marathon.namePoisk.set()

    @dp.message_handler(state=Marathon.namePoisk)
    async def process_namePoisk(message: types.Message, state: FSMContext):
        async with state.proxy() as marathonData:
            marathonData['namePoisk'] = message.text
        with open('doctor.txt', 'r') as f:
            appointments = f.read()
            found_appointments = appointments if marathonData['namePoisk'] in appointments else None
        if found_appointments:
            mes = f'Ваша запись на прием:\n{found_appointments}'
        else:
            mes = 'Вы не записывались!'
        await message.reply(mes, reply=False)
        await state.finish()

    @dp.message_handler(state=Marathon.distance)
    async def process_distance(message: types.Message, state: FSMContext):
        async with state.proxy() as marathonData:
            marathonData['distance'] = message.text
        text = f"Отлично, вы выбрали специалиста: {message.text}! Теперь выберите дату и время:"
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        for day, slots in available_slots.items():
            buttons.add(KeyboardButton(f'{day}: {" - ".join(slots)}'))
        await message.reply(text, reply_markup=buttons)
        await Marathon.datetime.set()

    @dp.message_handler(state=Marathon.datetime)
    async def process_datetime(message: types.Message, state: FSMContext):
        async with state.proxy() as marathonData:
            marathonData['datetime'] = message.text
        text = "Спасибо! Я сохранил ваши данные. Вы записаны на прием по следующим параметрам:"
        text += f"\nФИО: {marathonData['name']}"
        text += f"\nСпециалист: {marathonData['distance']}"
        text += f"\nДата и время: {marathonData['datetime']}"
        await message.reply(text, reply_markup=mainMenu)

        # Write data to the file
        with open('doctor.txt', 'a') as f:
            f.write(f"ФИО: {marathonData['name']}\n")
            f.write(f"Специалист: {marathonData['distance']}\n")
            f.write(f"Дата и время: {marathonData['datetime']}\n\n")

        await state.finish()

    executor.start_polling(dp, skip_updates=True)
