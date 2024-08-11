from dotenv import load_dotenv
import os
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '665691603'))
TRON_API_KEY = os.getenv('TRON_API_KEY')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
SENDER_ADDRESS = os.getenv('SENDER_ADDRESS')
USDT_TRC20_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"