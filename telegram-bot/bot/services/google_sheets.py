import gspread
from oauth2client.service_account import ServiceAccountCredentials
import asyncio
from bot.services.notification_manager import NotificationManager
from bot.services.logging_config import logger
from datetime import datetime

 

class GoogleSheetsClient:
    def __init__(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('taxi-628-fc905fe94865.json', scope)
        self.client = gspread.authorize(creds)
        
        self.drivers_sheet = self.client.open("Drivers").sheet1
        self.orders_sheet = self.client.open("Orders").sheet1
        self.notification_manager = NotificationManager()

    def append_driver(self, driver_data):
        try:
            logger.info(f"Appending driver data: {driver_data}")
            self.drivers_sheet.append_row(driver_data)
            logger.info("Driver data appended successfully")
        except Exception as e:
            logger.error(f"Error appending driver data: {e}")

    def get_orders(self, car_type):
        try:
            orders = self.orders_sheet.get_all_records()
            valid_orders = []
            status_filter_count = 0
            car_type_filter_count = 0
            datetime_filter_count = 0
            driver_filter_count = 0
            completeness_filter_count = 0

            for order in orders:
                logger.info(f"Processing order ID: {order['ID']}")

                # Проверка статуса заказа
                if order['статус'] != 'ищет водителя':
                    logger.info(f"Order ID {order['ID']} filtered out by status")
                    continue
                status_filter_count += 1

                # Проверка типа авто
                if order['класс'] != car_type:
                    logger.info(f"Order ID {order['ID']} filtered out by car type")
                    continue
                car_type_filter_count += 1

                # Проверка даты и времени заказа
                order_datetime = datetime.strptime(f"{order['дата']} {order['время']}", '%d.%m.%Y %H:%M')
                current_datetime = datetime.now()

                if order_datetime < current_datetime:
                    logger.info(f"Order ID {order['ID']} filtered out by date/time")
                    continue
                datetime_filter_count += 1

                # Проверка наличия водителя
                if order['ФИО водителя'] or order['ID водителя']:
                    logger.info(f"Order ID {order['ID']} filtered out by driver presence")
                    continue
                driver_filter_count += 1

                # Проверка заполненности всех значений
                if not all(order[key] for key in ['ID', 'статус', 'класс', 'маршрут полный заказа', 'стоимость', 'дата', 'время', 'ФИО клиента', 'номер клиента', 'примечание к заказу']):
                    logger.info(f"Order ID {order['ID']} filtered out by completeness")
                    continue
                completeness_filter_count += 1

                valid_orders.append(order)
            
            logger.info(f"Filtered orders: {valid_orders}")
            logger.info(f"Status filter passed: {status_filter_count}")
            logger.info(f"Car type filter passed: {car_type_filter_count}")
            logger.info(f"Date/time filter passed: {datetime_filter_count}")
            logger.info(f"Driver filter passed: {driver_filter_count}")
            logger.info(f"Completeness filter passed: {completeness_filter_count}")
            return valid_orders
        except Exception as e:
            logger.error(f"Error retrieving orders: {e}")
            return []




    # def get_driver_info(self, user_id):
    #     try:
    #         drivers = self.drivers_sheet.get_all_records()
    #         for driver in drivers:
    #             if driver['user_id'] == user_id:
    #                 logger.info(f"Driver found: {driver['full_name']} with user_id: {user_id}")
    #                 return driver['full_name'], user_id
    #         logger.warning(f"No driver found with user_id: {user_id}")
    #         return None, None
    #     except Exception as e:
    #         logger.error(f"Error retrieving driver info: {e}")
    #         return None, None



    def get_driver_car_type(self, user_id):
            try:
                drivers = self.drivers_sheet.get_all_records()
                for driver in drivers:
                    if driver['user_id'] == user_id:
                        return driver['car_type']
                return None
            except Exception as e:
                logger.error(f"Error retrieving car type for user_id {user_id}: {e}")
                return None


    def update_order_type(self, order_id, car_type):
        try:
            cell = self.orders_sheet.find(order_id)
            self.orders_sheet.update_cell(cell.row, self.orders_sheet.find('класс').col, car_type)
            logger.info(f"Order {order_id} car type updated to {car_type}")
        except Exception as e:
            logger.error(f"Error updating order {order_id} car type: {e}")


    def get_order_by_id(self, order_id):
        try:
            cell = self.orders_sheet.find(order_id)
            order = self.orders_sheet.row_values(cell.row)
            order_dict = dict(zip(self.orders_sheet.row_values(1), order))
            return order_dict
        except Exception as e:
            logger.error(f"Error retrieving order {order_id}: {e}")
            return None


            

    def get_user_orders(self, user_id):
        try:
            orders = self.orders_sheet.get_all_records()
            user_orders = [order for order in orders if order['ID водителя'] == user_id and order['статус'] == 'назначен водитель']
            return user_orders
        except Exception as e:
            logger.error(f"Error retrieving user orders for user_id {user_id}: {e}")
            return []
    def complete_order(self, order_id):
        try:
            cell = self.orders_sheet.find(order_id)
            self.orders_sheet.update_cell(cell.row, self.orders_sheet.find('статус').col, 'выполнен')
            logger.info(f"Order {order_id} status updated to 'выполнен'")
        except Exception as e:
            logger.error(f"Error completing order {order_id}: {e}")




    def update_order_status(self, order_id, status, driver_name, driver_id):
        try:
            valid_statuses = ["ищет водителя", "назначен водитель", "выполнен"]
            if status not in valid_statuses:
                raise ValueError(f"Invalid status: {status}")
            cell = self.orders_sheet.find(order_id)
            self.orders_sheet.update_cell(cell.row, self.orders_sheet.find('статус').col, status)
            self.orders_sheet.update_cell(cell.row, self.orders_sheet.find('ФИО водителя').col, driver_name)
            self.orders_sheet.update_cell(cell.row, self.orders_sheet.find('ID водителя').col, driver_id)
            logger.info(f"Order {order_id} status updated to {status}")
        except Exception as e:
            logger.error(f"Error updating order {order_id} status: {e}")



    async def monitor_driver_types(self):
        previous_data = self.drivers_sheet.get_all_records()
        while True:
            await asyncio.sleep(10)  # Проверяем каждые 10 секунд
            current_data = self.drivers_sheet.get_all_records()
            for prev, curr in zip(previous_data, current_data):
                if prev['car_type'] != curr['car_type'] and curr['car_type']:
                    await self.notification_manager.send_registration_complete(curr['user_id'], curr['car_type'])
            previous_data = current_data


    def get_driver_info(self, user_id):
        try:
            drivers = self.drivers_sheet.get_all_records()
            for driver in drivers:
                if driver['user_id'] == user_id:
                    return driver['full_name'], driver['phone_number'], driver['car_brand'], driver['car_color'], driver['license_plate'], driver['body_type'], driver['year'], user_id, driver['car_type']
            return None, None, None, None, None, None, None, None
        except Exception as e:
            logger.error(f"Error retrieving driver info for user_id {user_id}: {e}")
            return None, None, None, None, None, None, None, None
