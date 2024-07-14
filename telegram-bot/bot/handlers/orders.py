from aiogram import types
from bot_initialization import dp
from bot.services.google_sheets import GoogleSheetsClient

google_sheets_client = GoogleSheetsClient()

@dp.message_handler(commands=['orders'])
async def list_orders(message: types.Message):
    car_type = "Эконом"  # Измените на актуальный тип авто для тестирования
    orders = google_sheets_client.get_orders(car_type)
    if orders:
        for order in orders:
            order_info = (f"Номер заказа: {order['ID']}\n"
                          f"Маршрут: {order['маршрут полный заказа']}\n"
                          f"Стоимость: {order['стоимость']}\n"
                          f"Дата: {order['дата']}\n"
                          f"Время: {order['время']}\n"
                          f"Приченание к заказу: {order['примечание к заказу']}")
            await message.reply(order_info)
    else:
        await message.reply("No orders available.")
