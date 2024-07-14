from aiogram import Bot
from bot.services.config import TELEGRAM_TOKEN

class NotificationManager:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_TOKEN)

    async def send_registration_complete(self, chat_id, car_type):
        await self.bot.send_message(chat_id, f" Вашему автомобилю присвоен тип {car_type}.")

    async def send_type_changed(self, chat_id, new_car_type):
        await self.bot.send_message(chat_id, f"Тип вашего авто изменен на {new_car_type}.")

    async def send_new_order(self, chat_id, order_info):
        await self.bot.send_message(chat_id, f"У вас новый заказ: {order_info}")
