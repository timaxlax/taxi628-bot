from aiogram import types, Dispatcher
from bot.services.logging_config import logger

def register_error_handlers(dp: Dispatcher):
    @dp.errors_handler()
    async def errors_handler(update, exception):
        logger.error(f'Update {update} caused error {exception}')
        return True

# Регистрация обработчиков ошибок
from bot_initialization import dp
register_error_handlers(dp)
