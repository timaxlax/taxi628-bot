from aiogram.utils.executor import start_polling
from bot_initialization import bot, dp
from bot.services.logging_config import logger
import bot.services.error_handler  # импортируем, чтобы зарегистрировать обработчики ошибок
from bot.services.google_sheets import GoogleSheetsClient
import asyncio

# Импортируем обработчики команд
import bot.handlers.start
import bot.handlers.orders
import bot.handlers.cancel
import bot.handlers.help
import bot.handlers.support
import bot.handlers.unknown
import bot.handlers.manager

async def on_startup(dp):
    google_sheets_client = GoogleSheetsClient()
    asyncio.create_task(google_sheets_client.monitor_driver_types())

if __name__ == '__main__':
    logger.info("Starting bot")
    start_polling(dp, skip_updates=True, on_startup=on_startup)
