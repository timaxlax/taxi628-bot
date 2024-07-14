from aiogram import types
from aiogram.dispatcher import Dispatcher
from bot.main import bot, dp

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    help_text = (
        "Доступные команды:\n"
        "/start - Начало работы с ботом\n"
        "/orders - Получить список доступных заказов\n"
        "/cancel - Отмена текущего действия\n"
        "/support - Связаться с техподдержкой\n"
        "/help - Показать это сообщение"
    )
    await message.reply(help_text)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)
