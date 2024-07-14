from aiogram import types
from bot_initialization import dp

@dp.message_handler(commands=['support'])
async def support_command(message: types.Message):
    await message.reply("Для поддержки свяжитесь с менеджером: manager@example.com или позвоните по телефону: +123456789")
