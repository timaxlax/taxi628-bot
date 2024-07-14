import gspread
from oauth2client.service_account import ServiceAccountCredentials
import asyncio
from bot.services.notification_manager import NotificationManager
from bot.services.logging_config import logger

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
        orders = self.orders_sheet.get_all_records()
        valid_orders = [order for order in orders if order['класс'] == car_type and order['статус'] == 'ищет водителя']
        logger.info(f"Filtered orders: {valid_orders}")
        return valid_orders

    def update_order_status(self, order_id, status, driver_name):
        try:
            valid_statuses = ["ищет водителя", "назначен водитель", "выполнен"]
            if status not in valid_statuses:
                raise ValueError(f"Invalid status: {status}")
            cell = self.orders_sheet.find(order_id)
            self.orders_sheet.update_cell(cell.row, self.orders_sheet.find('статус').col, status)
            if driver_name:
                self.orders_sheet.update_cell(cell.row, self.orders_sheet.find('ФИО водителя').col, driver_name)
            logger.info(f"Order {order_id} status updated to {status}")
        except Exception as e:
            logger.error(f"Error updating order {order_id} status: {e}")

    def update_order_type(self, order_id, car_type):
        try:
            cell = self.orders_sheet.find(order_id)
            self.orders_sheet.update_cell(cell.row, self.orders_sheet.find('класс').col, car_type)
            logger.info(f"Order {order_id} car type updated to {car_type}")
        except Exception as e:
            logger.error(f"Error updating order {order_id} car type: {e}")

    async def monitor_driver_types(self):
        previous_data = self.drivers_sheet.get_all_records()
        while True:
            await asyncio.sleep(10)  # Проверяем каждые 10 секунд
            current_data = self.drivers_sheet.get_all_records()
            for prev, curr in zip(previous_data, current_data):
                if prev['car_type'] != curr['car_type'] and curr['car_type']:
                    await self.notification_manager.send_registration_complete(curr['user_id'], curr['car_type'])
            previous_data = current_data
