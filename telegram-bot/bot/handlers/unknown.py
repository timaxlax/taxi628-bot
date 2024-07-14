from aiogram import types
from aiogram.dispatcher import Dispatcher
from bot.main import bot, dp

@dp.message_handler()
async def unknown_command(message: types.Message):
    await message.reply("Неизвестная команда. Пожалуйста, используйте /help для списка доступных команд.")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)
