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
    else:
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
