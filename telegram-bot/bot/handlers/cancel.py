from aiogram import types
from aiogram.dispatcher import Dispatcher
from bot.main import bot, dp

@dp.message_handler(commands=['cancel'])
async def cancel_command(message: types.Message):
    await message.reply("Действие отменено.")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)
