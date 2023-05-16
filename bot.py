from aiogram import Bot, Dispatcher, executor, types

TOKEN_API = "6292399749:AAEL2xgOXJGC7NnFtUMu1xujM6upo8FxZ2M"

bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

def TeleBot():
    # Создаем клавиатуру
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Добавляем кнопку, при нажатии на которую появятся еще три кнопки
    more_button = types.KeyboardButton('Запись на прием')
    keyboard.add(more_button)

    # Добавляем еще три кнопки
    button1 = types.KeyboardButton('Ввод ФИО')
    button2 = types.KeyboardButton("Врач")

    # Обработчик команды /start
    @dp.message_handler(commands=['start'])
    async def process_start_command(message: types.Message):
        # Отправляем сообщение с кнопкой
        await message.reply("Нажмите на кнопку, чтобы появились еще три кнопки", reply_markup=keyboard)

    # Обработчик нажатия на кнопку "Запись на прием"
    @dp.message_handler(lambda message: message.text == 'Запись на прием')
    async def process_more_button(message: types.Message):
        # Отправляем сообщение с тремя кнопками
        await message.reply("Выберите действие",
                            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).row(button1, button2))

    # Обработчик нажатия на кнопку "Врач"
    @dp.message_handler(lambda message: message.text == 'Врач')
    async def process_doctor_button(message: types.Message):
        # Отправляем сообщение с инлайн кнопками
        inline_keyboard = types.InlineKeyboardMarkup()
        inline_keyboard.add(
            types.InlineKeyboardButton('Хирург', callback_data='Хирург'),
            types.InlineKeyboardButton('Терапевт', callback_data='Терапевт'),
            types.InlineKeyboardButton('Стоматолог', callback_data='Стоматолог'),
            types.InlineKeyboardButton('Дерматолог', callback_data='Дерматолог')
        )
        await bot.send_message(chat_id=message.chat.id, text='Выберите врача:', reply_markup=inline_keyboard)

    # Обработчик нажатия на инлайн кнопку
    @dp.callback_query_handler(lambda c: c.data)
    async def process_callback_button(callback_query: types.CallbackQuery):
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(chat_id=callback_query.from_user.id, text=f'Вы выбрали врача {callback_query.data}')

    executor.start_polling(dp, skip_updates=True)