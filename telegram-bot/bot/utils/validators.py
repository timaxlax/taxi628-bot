import re

def is_valid_phone_number(phone_number):
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone_number) is not None

def is_valid_license_plate(license_plate):
    pattern = r'^[A-Z0-9-]{1,10}$'
    return re.match(pattern, license_plate) is not None

def is_valid_year(year):
    return year.isdigit() and 1900 <= int(year) <= 2100
