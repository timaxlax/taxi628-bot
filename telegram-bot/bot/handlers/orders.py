
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_initialization import dp
from bot.services.google_sheets import GoogleSheetsClient
from bot.services.logging_config import logger

google_sheets_client = GoogleSheetsClient()

 
class OrderConfirmation(StatesGroup):
    order_id = State()
    order_info = State()

class OrderStates(StatesGroup):
    order_action = State()


async def show_cancel_button(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_cancel = KeyboardButton("Отмена")
    markup.add(button_cancel)
    await message.answer("Для отмены действия нажмите 'Отмена'.", reply_markup=markup)


@dp.message_handler(commands=['orders'])
async def list_orders(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    car_type = google_sheets_client.get_driver_car_type(user_id)
    
    if not car_type:
        await message.reply("Не удалось найти тип вашего авто. Пожалуйста, зарегистрируйтесь или свяжитесь с поддержкой.")
        return
    
    orders = google_sheets_client.get_orders(car_type)
    if orders:
        messages_to_delete = []
        for order in orders:
            order_info = (f"Номер заказа: {order['ID']}\n"
                          f"Маршрут: {order['маршрут полный заказа']}\n"
                          f"Стоимость: {order['стоимость']}\n"
                          f"Дата: {order['дата']}\n"
                          f"Время: {order['время']}\n"
                          f"Примечание к заказу: {order['примечание к заказу']}")
            markup = InlineKeyboardMarkup()
            button = InlineKeyboardButton("Выбрать", callback_data=f"select_order_{order['ID']}")
            markup.add(button)
            msg = await message.reply(order_info, reply_markup=markup)
            messages_to_delete.append(msg.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        await show_cancel_button(message)
        await OrderStates.order_action.set()
    else:
        await message.reply("Нет доступных заказов для вашего типа авто.")



@dp.callback_query_handler(lambda c: c.data and c.data.startswith('select_order_'))
async def process_select_order(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"Select order callback data: {callback_query.data}")
    order_id = callback_query.data.split('_')[2]
    order_info = await get_order_info(order_id)
    
    data = await state.get_data()
    messages_to_delete = data.get('messages_to_delete', [])
    for message_id in messages_to_delete:
        await dp.bot.delete_message(callback_query.from_user.id, message_id)

    markup = InlineKeyboardMarkup()
    button_yes = InlineKeyboardButton("Да", callback_data=f"confirm_order_{order_id}")
    button_no = InlineKeyboardButton("Нет", callback_data="cancel_order")
    markup.add(button_yes, button_no)
    
    confirmation_message = await dp.bot.send_message(callback_query.from_user.id, f"Вы уверены, что хотите взять заказ:\n{order_info}", reply_markup=markup)
    await OrderConfirmation.order_id.set()
    await state.update_data(order_id=order_id, order_info=order_info, confirmation_message_id=confirmation_message.message_id)












@dp.message_handler(commands=['my_orders'])
async def list_user_orders(message: types.Message):
    user_id = message.from_user.id
    orders = google_sheets_client.get_user_orders(user_id)
    
    if orders:
        for order in orders:
            order_info = (f"Номер заказа: {order['ID']}\n"
                          f"Маршрут: {order['маршрут полный заказа']}\n"
                          f"Стоимость: {order['стоимость']}\n"
                          f"Дата: {order['дата']}\n"
                          f"Время: {order['время']}\n"
                          f"ФИО клиента: {order['ФИО клиента']}\n"
                          f"Номер клиента: {order['номер клиента']}\n"
                          f"Примечание к заказу: {order['примечание к заказу']}")
            markup = InlineKeyboardMarkup()
            button = InlineKeyboardButton("Завершить заказ", callback_data=f"complete_order_{order['ID']}")
            markup.add(button)
            await message.reply(order_info, reply_markup=markup)
        await show_cancel_button(message)
        await OrderStates.order_action.set()
    else:
        await message.reply("У вас нет взятых заказов.")


    

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('complete_order_'))
async def process_complete_order(callback_query: types.CallbackQuery):
    logger.info(f"Complete order callback data: {callback_query.data}")
    order_id = callback_query.data.split('_')[2]

    try:
        google_sheets_client.complete_order(order_id)
        await callback_query.message.delete()
        await dp.bot.send_message(callback_query.from_user.id, f"Заказ {order_id} завершен.")
    except Exception as e:
        logger.error(f"Error completing order {order_id}: {e}")
        await dp.bot.send_message(callback_query.from_user.id, "Произошла ошибка при завершении заказа. Пожалуйста, попробуйте снова.")





@dp.callback_query_handler(lambda c: c.data == 'cancel_order', state=OrderConfirmation.order_id)
async def process_cancel_order(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"Cancel order callback data: {callback_query.data}")
    data = await state.get_data()
    confirmation_message_id = data.get('confirmation_message_id')
    await dp.bot.delete_message(callback_query.from_user.id, confirmation_message_id)
    await callback_query.answer("Выберите заказ заново.")
    await state.finish()




@dp.callback_query_handler(lambda c: c.data and c.data.startswith('confirm_order_'), state=OrderConfirmation.order_id)
async def process_confirm_order(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"Confirm order callback data: {callback_query.data}")
    data = await state.get_data()
    order_id = data['order_id']
    order_info = data['order_info']
    
    driver_info  = google_sheets_client.get_driver_info(callback_query.from_user.id)
    logger.info(f"Confirm order callback data: {driver_info[0], callback_query.from_user.id}")
    if not driver_info[0]:
        logger.warning(f"Driver info not found for user_id: {callback_query.from_user.id}")
        await callback_query.answer("Не удалось найти данные водителя. Пожалуйста, зарегистрируйтесь.")
        await state.finish()
        return

    try:
        google_sheets_client.update_order_status(order_id, "назначен водитель", driver_info[0], callback_query.from_user.id)
        await dp.bot.send_message(callback_query.from_user.id, f"Вы взяли заказ:\n{order_info}")
        
        # Удаление сообщения подтверждения
        confirmation_message_id = data.get('confirmation_message_id')
        await dp.bot.delete_message(callback_query.from_user.id, confirmation_message_id)
        
        # Получаем данные клиента
        order = google_sheets_client.get_order_by_id(order_id)
        client_info = (f"ФИО клиента: {order['ФИО клиента']}\n"
                       f"Номер клиента: {order['номер клиента']}")
        await dp.bot.send_message(callback_query.from_user.id, f"Данные клиента:\n{client_info}")
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        await dp.bot.send_message(callback_query.from_user.id, "Произошла ошибка при обновлении заказа. Пожалуйста, попробуйте снова.")
    
    await state.finish()



@dp.callback_query_handler(lambda c: c.data == 'cancel_order', state=OrderStates.order_action)
async def process_cancel_order(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.answer("Выберите заказ заново.")
    await show_main_menu(callback_query.message)
    await state.finish()


async def get_order_info(order_id):
    order = google_sheets_client.get_order_by_id(order_id)
    order_info = (f"Номер заказа: {order['ID']}\n"
                  f"Маршрут: {order['маршрут полный заказа']}\n"
                  f"Стоимость: {order['стоимость']}\n"
                  f"Дата: {order['дата']}\n"
                  f"Время: {order['время']}\n"
                  f"Примечание к заказу: {order['примечание к заказу']}")
    return order_info


