import asyncio
from aiogram import types
from aiogram.dispatcher import Dispatcher
from bot.services.google_sheets import GoogleSheetsClient
from bot.services.notification_manager import NotificationManager
from bot.main import bot, dp

google_sheets_client = GoogleSheetsClient()
notification_manager = NotificationManager()

async def check_driver_status():
    while True:
        await asyncio.sleep(10)  # Ждем 1 минуту перед проверкой
        orders_sheet = google_sheets_client.get_orders_sheet()
        orders = orders_sheet.get_all_records()

        for order in orders:
            if 'car_type' in order and order['car_type']:
                driver_chat_id = order.get('user_id')
                if driver_chat_id:
                    await notification_manager.send_registration_complete(driver_chat_id, order['car_type'])
                orders_sheet.update_cell(order['номер заказа'], 'user_id', '')  # Очищаем поле user_id

@dp.message_handler(commands=['assign_type'])
async def assign_type_command(message: types.Message):
    await message.reply("Введите номер заказа и тип авто через запятую:")

@dp.message_handler(lambda message: ',' in message.text)
async def process_assign_type(message: types.Message):
    data = message.text.split(',')
    if len(data) == 2:
        order_id, car_type = data
        google_sheets_client.update_order_status(order_id.strip(), 'Тип авто назначен', '')
        google_sheets_client.update_order_type(order_id.strip(), car_type.strip())
        await message.reply("Тип авто назначен.")
    else:
        await message.reply("Пожалуйста, введите данные в формате: Номер заказа, тип авто.")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)
