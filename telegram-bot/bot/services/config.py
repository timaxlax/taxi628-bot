import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GOOGLE_SHEETS_KEYFILE = os.getenv('GOOGLE_SHEETS_KEYFILE')
