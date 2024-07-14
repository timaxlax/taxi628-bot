from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot_initialization import dp
from bot.services.google_sheets import GoogleSheetsClient
from bot.services.google_sheets import GoogleSheetsClient
from bot.services.notification_manager import NotificationManager
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from bot.handlers.orders import list_user_orders, list_orders  # Импорт функций из orders.py

class Registration(StatesGroup):
    agreement = State()
    full_name = State()
    phone_number = State()
    car_brand = State()
    car_color = State()
    license_plate = State()
    body_type = State()
    year = State()


google_sheets_client = GoogleSheetsClient()
notification_manager = NotificationManager()



@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    driver_info = google_sheets_client.get_driver_info(user_id)
    if driver_info[0] is not None:
        await message.reply(f"Вы уже зарегистрированы. Вот ваши данные:\n"
                            f"ФИО: {driver_info[0]}\n"
                            f"Номер телефона: {driver_info[1]}\n"
                            f"Марка автомобиля: {driver_info[2]}\n"
                            f"Цвет автомобиля: {driver_info[3]}\n"
                            f"Гос. номер автомобиля: {driver_info[4]}\n"
                            f"Тип кузова: {driver_info[5]}\n"
                            f"Год выпуска: {driver_info[6]}\n"
                            f"Тип авто: {driver_info[7]}")
        await show_main_menu(message)
    else:
        await message.reply("Добро пожаловать! Пожалуйста, ознакомьтесь с лицензионным соглашением по ссылке ниже и выберите, принимаете ли вы его.")
        markup = InlineKeyboardMarkup()
        button_accept = InlineKeyboardButton("Принимаю", callback_data="accept_agreement")
        button_decline = InlineKeyboardButton("Не принимаю", callback_data="decline_agreement")
        markup.add(button_accept, button_decline)
        await message.reply("Лицензионное соглашение: [ссылка](https://example.com/agreement)", reply_markup=markup)
        await Registration.agreement.set()




@dp.callback_query_handler(lambda c: c.data == 'decline_agreement', state=Registration.agreement)
async def decline_agreement(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Для работы нужно принять лицензионное соглашение.")
    markup = InlineKeyboardMarkup()
    button_accept = InlineKeyboardButton("Принимаю", callback_data="accept_agreement")
    button_decline = InlineKeyboardButton("Не принимаю", callback_data="decline_agreement")
    markup.add(button_accept, button_decline)
    await callback_query.message.answer("Лицензионное соглашение: [ссылка](https://example.com/agreement)", reply_markup=markup)






@dp.callback_query_handler(lambda c: c.data == 'accept_agreement', state=Registration.agreement)
async def accept_agreement(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.message.answer("Пожалуйста, введите ваше ФИО:")
    await Registration.full_name.set()

@dp.message_handler(state=Registration.full_name)
async def get_full_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['full_name'] = message.text
    await message.reply("Введите ваш номер телефона:")
    await Registration.next()

@dp.message_handler(state=Registration.phone_number)
async def get_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text
    await message.reply("Введите марку вашего автомобиля:")
    await Registration.next()

@dp.message_handler(state=Registration.car_brand)
async def get_car_brand(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['car_brand'] = message.text
    await message.reply("Введите цвет вашего автомобиля:")
    await Registration.next()

@dp.message_handler(state=Registration.car_color)
async def get_car_color(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['car_color'] = message.text
    await message.reply("Введите гос. номер вашего автомобиля:")
    await Registration.next()

@dp.message_handler(state=Registration.license_plate)
async def get_license_plate(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['license_plate'] = message.text
    await message.reply("Введите тип кузова вашего автомобиля:")
    await Registration.next()

@dp.message_handler(state=Registration.body_type)
async def get_body_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['body_type'] = message.text
    await message.reply("Введите год выпуска вашего автомобиля:")
    await Registration.next()

@dp.message_handler(state=Registration.year)
async def getyear(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['year'] = message.text
        driverdata = [
            data['full_name'],
            data['phone_number'],
            data['car_brand'],
            data['car_color'],
            data['license_plate'],
            data['body_type'],
            data['year'],
            message.from_user.id,
        ]
        google_sheets_client.append_driver(driverdata)
    await message.reply("Ваша заявка на регистрацию рассматривается менеджером. Пожалуйста, подождите.")
    await state.finish()
    await show_main_menu(message)




async def show_main_menu(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_my_orders = KeyboardButton("Мои заказы")
    button_all_orders = KeyboardButton("Актуальные заказы")
    button_help = KeyboardButton("Помощь")
    button_support = KeyboardButton("Связь с менеджером")
    button_profile = KeyboardButton("Профиль")
    markup.add(button_help, button_support, button_profile, button_my_orders, button_all_orders)
    await message.answer("Добро пожаловать в главное меню:", reply_markup=markup)

@dp.message_handler(lambda message: message.text == "Актуальные заказы")
async def handle_all_orders(message: types.Message, state: FSMContext):
    await list_orders(message, state)

@dp.message_handler(lambda message: message.text == "Мои заказы")
async def handle_my_orders(message: types.Message):
    await list_user_orders(message)



@dp.message_handler(lambda message: message.text == "Помощь")
async def handle_help(message: types.Message):
    await message.reply("Здесь будет информация о помощи.")

@dp.message_handler(lambda message: message.text == "Связь с менеджером")
async def handle_support(message: types.Message):
    await message.reply("Здесь будет информация о связи с поддержкой.")


@dp.message_handler(lambda message: message.text == "Отмена")
async def handle_cancel(message: types.Message):
    await message.reply("Действие отменено.")
    await show_main_menu(message)

@dp.message_handler(lambda message: message.text == "Профиль")
async def handle_cancel(message: types.Message):
    await message.reply("Ваш профиль:")
    await start_command(message)

