from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot_initialization import dp
from bot.services.google_sheets import GoogleSheetsClient
from bot.services.notification_manager import NotificationManager

class Registration(StatesGroup):
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
    await message.reply("Добро пожаловать! Пожалуйста, введите ваше ФИО:")
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
async def get_year(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['year'] = message.text
        driver_data = [
            data['full_name'],
            data['phone_number'],
            data['car_brand'],
            data['car_color'],
            data['license_plate'],
            data['body_type'],
            data['year'],
            message.from_user.id,
        ]
        google_sheets_client.append_driver(driver_data)
    await message.reply("Ваша заявка на регистрацию рассматривается менеджером. Пожалуйста, подождите.")
    await state.finish()
