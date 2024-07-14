from bot.services.google_sheets import GoogleSheetsClient

 
class OrderManager:
    def __init__(self):
        self.google_sheets_client = GoogleSheetsClient()

    def get_active_orders(self, car_type):
        orders = self.google_sheets_client.get_orders(car_type)
        return [order for order in orders if order['статус'] == 'ищет водителя']

    def update_order_status(self, order_id, status, driver_name):
        self.google_sheets_client.update_order_status(order_id, status, driver_name)

    def filter_orders(self, orders, car_type):
        # Пример фильтрации заказов по типу автомобиля и другим параметрам
        filtered_orders = []
        for order in orders:
            if order['тип авто'] == car_type and order['статус'] == 'ищет водителя':
                filtered_orders.append(order)
        return filtered_orders

