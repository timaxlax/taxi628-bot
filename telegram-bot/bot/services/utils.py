def is_valid_phone_number(phone_number):
    # Простой пример проверки номера телефона
    return phone_number.isdigit() and len(phone_number) >= 10
