from telegram import Update
from telegram.ext import Application, PicklePersistence, CommandHandler, CallbackQueryHandler, ConversationHandler, filters, MessageHandler
from config import TELEGRAM_BOT_TOKEN
from handlers import start, check_balance, withdraw_start, receive_wallet_address, receive_amount_to_withdraw, \
    approve_withdrawal, cancel, help_command, menu, menu_button_handler, ADDRESS, AMOUNT, APPROVE, USERNAME, \
    increase_balance, receive_username, receive_amount_to_increase
from utilities import create_table

def main() -> None:
    create_table()
    persistence = PicklePersistence(filepath="callbackdatabot")
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .persistence(persistence)
        .arbitrary_callback_data(True)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler('menu', menu))
    application.add_handler(CommandHandler('check_balance', check_balance))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(menu_button_handler))

    conv_handler_increase = ConversationHandler(
        entry_points=[CommandHandler('increase_balance', increase_balance)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_username)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount_to_increase)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(conv_handler_increase)

    conv_handler_withdraw = ConversationHandler(
        entry_points=[CommandHandler('withdraw', withdraw_start)],
        states={
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_wallet_address)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount_to_withdraw)],
            APPROVE: [CallbackQueryHandler(approve_withdrawal, pattern='approve_withdrawal'),
                      CallbackQueryHandler(cancel, pattern='cancel')]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler_withdraw)
    application.add_handler(CallbackQueryHandler(menu_button_handler, pattern='^check_balance$|^withdraw$|^help$'))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()


# import logging
# from typing import List, Tuple, cast
#
# from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
# from telegram.ext import (
#     Application,
#     CallbackQueryHandler,
#     CommandHandler,
#     ConversationHandler,
#     ContextTypes,
#     MessageHandler,
#     filters,
#     InvalidCallbackData,
#     PicklePersistence,
# )
# import sqlite3
# from tronpy import Tron
# from tronpy.keys import PrivateKey
# from tronpy.providers import HTTPProvider
#
#
# # Enable logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# # State definitions for conversation handler
# USERNAME, AMOUNT, ADDRESS, APPROVE = range(4)
#
# # Telegram bot token
# TELEGRAM_BOT_TOKEN = '7462320868:AAGEyS6S376GHIIZ9fBa8Ro22zfXkIkOZqw'
# # PRIVATE_KEY = "69f68c2dc53f5487628aeeffb2babe48a87c479ab18ef605828a12dffeaf019a"
# PRIVATE_KEY = "1aba70a42fa8420c742dfa529c9fa36500a83f942479f668509232ff6eed8e44"
# ADMIN_ID = 665691603
#
# client = Tron(HTTPProvider(api_key="cde7bff2-ca39-4c5a-a6a5-7c0d7434cd30"))  # Use mainnet(trongrid) with a single api_key
#
# # Your private key
# private_key_tron = PrivateKey(bytes.fromhex(PRIVATE_KEY))
# # sender_address_tron = "TUsxvzPSVfPKGi183gH1zDf18DcmNJVzY7"
# sender_address_tron = "TV1gMPWRT44Ft4h8akeGnXa4mHWZeZwn7L"
#
# # derived_address = private_key_tron.public_key.to_base58check_address()
# # print(f"Derived Address: {derived_address}")
# class User:
#     def __init__(self, telegram_id, username):
#         self.telegram_id = telegram_id
#         self.username = username
#
#     @staticmethod
#     def get_user_by_username(username):
#         conn = sqlite3.connect('employees.db')
#         c = conn.cursor()
#         c.execute('SELECT telegram_id, balance FROM employees WHERE username = ?', (username,))
#         row = c.fetchone()
#         conn.close()
#         if row:
#             return User(row[0], username)
#         else:
#             return None
#
#     def get_user_by_telegram_id(telegram_id):
#         conn = sqlite3.connect('employees.db')
#         c = conn.cursor()
#         c.execute('SELECT username, balance FROM employees WHERE telegram_id = ?', (telegram_id,))
#         row = c.fetchone()
#         conn.close()
#         if row:
#             return User(telegram_id, row[0])
#         else:
#             return None
#
#     def update_balance(self, amount):
#         conn = sqlite3.connect('employees.db')
#         c = conn.cursor()
#         c.execute('UPDATE employees SET balance = ? WHERE telegram_id = ?', (amount, self.telegram_id))
#         conn.commit()
#         conn.close()
#
#     def get_balance(self):
#         conn = sqlite3.connect('employees.db')
#         c = conn.cursor()
#         c.execute('SELECT balance FROM employees WHERE telegram_id = ?', (self.telegram_id,))
#         row = c.fetchone()
#         conn.close()
#         if row:
#             return row[0]
#         else:
#             return 0.0
#
#
# async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Initiate the withdrawal process."""
#     logger.info(f"User {update.message.from_user.id} started withdrawal process.")
#     await update.message.reply_text('Please enter your USDT wallet address:')
#     return ADDRESS
#
# async def receive_wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Receive the wallet address and ask for the amount."""
#     employee_wallet_address = update.message.text
#
#     try:
#         # Validate wallet address
#         context.user_data['wallet_address'] = employee_wallet_address
#         logger.info(f"User {update.message.from_user.id} provided wallet address: {employee_wallet_address}")
#         await update.message.reply_text('Please enter the amount of USDT you want to withdraw:')
#         return AMOUNT
#     except ValueError as e:
#         await update.message.reply_text(str(e) + " Please enter a valid Ethereum address.")
#         logger.warning(f"User {update.message.from_user.id} provided invalid wallet address: {employee_wallet_address}")
#         return ADDRESS
#
# async def receive_amount_to_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Receive the amount and process the withdrawal."""
#     try:
#         user_id = update.message.from_user.id
#         user = User.get_user_by_telegram_id(user_id)
#         balance = user.get_balance()
#         usdt_amount = float(update.message.text)
#         if usdt_amount <= 0:
#             raise ValueError("Amount must be greater than zero.")
#         if usdt_amount > balance:
#             raise ValueError(f"You have only {balance} on your balance")
#         # Convert amount to smallest unit (wei for Ethereum)
#         amount_in_wei = int(usdt_amount * 10 ** 6)
#         logger.info(f"User {update.message.from_user.id} wants to withdraw {usdt_amount} USDT from his balance {balance}.")
#     except ValueError:
#         await update.message.reply_text("Invalid amount. Please enter a numeric value.")
#         logger.warning(f"User {update.message.from_user.id} provided invalid amount: {update.message.text}")
#         return AMOUNT
#
#     employee_wallet_address = context.user_data.get('wallet_address')
#     #checksum_employee_wallet_address = web3.to_checksum_address(employee_wallet_address)
#
#
#     logger.info(f"address of reciever is {employee_wallet_address}")
#
#     try:
#         usdt_contract = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
#         contract = client.get_contract(usdt_contract)
#
#
#         txn = (
#             contract.functions.transfer(employee_wallet_address, amount_in_wei)
#             .with_owner(sender_address_tron)
#             .fee_limit(20_000_000)
#             .build()
#             .sign(private_key_tron)
#         )
#         txn.broadcast().wait()
#         logger.info("transaction accepted", txn.broadcast().result())
#         # Broadcast the transaction
#         logger.info(txn)
#         logger.info(txn.txid)
#
#         await update.message.reply_text(f"Withdrawal of {usdt_amount} USDT to {employee_wallet_address} initiated. Transaction id {txn.txid} and broadcast {txn.broadcast().wait()}")
#         logger.info(f"User {update.message.from_user.id} successfully withdrew {usdt_amount} USDT to {employee_wallet_address}. Transaction id {txn.txid} and broadcast {txn.broadcast().wait()}")
#     except Exception as e:
#         await update.message.reply_text(f"An error occurred: {str(e)}")
#         logger.error(f"Error during withdrawal for user {update.message.from_user.id}: {str(e)}")
#
#     return ConversationHandler.END
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     user_id = update.message.from_user.id
#     username = update.message.from_user.username
#     conn = sqlite3.connect('employees.db')
#     c = conn.cursor()
#     c.execute('''
#            INSERT INTO employees (telegram_id, username, balance)
#            VALUES (?, ?, 0)
#            ON CONFLICT(telegram_id)
#            DO UPDATE SET username = excluded.username
#        ''', (user_id, username))
#     conn.commit()
#     conn.close()
#     await update.message.reply_text('Welcome!')
#
# async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     user_id = update.message.from_user.id
#     user = User.get_user_by_telegram_id(user_id)
#     if user:
#         balance = user.get_balance()
#         await update.message.reply_text(f'Your balance is: {balance} USDT')
#     else:
#         await update.message.reply_text('No balance found.')
#
#
#
# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     await update.message.reply_text('Withdrawal process cancelled.')
#     logger.info(f"User {update.message.from_user.id} cancelled the withdrawal process.")
#     return ConversationHandler.END
#
# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     help_text = (
#         "Here are the available commands:\n"
#         "/start - Start the bot and register your username.\n"
#         "/check_balance - Check your current USDT balance.\n"
#         "/increase_balance - Admin command to increase the balance of an employee.\n"
#         "/cancel - Cancel any ongoing operations.\n"
#         "/help - Show this help message."
#     )
#     await update.message.reply_text(help_text)
#
#
# async def increase_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     # Check if the command is issued by the admin
#     if update.message.from_user.id == ADMIN_ID:
#         await update.message.reply_text('Please enter the username of the employee whose balance you want to increase:')
#         return USERNAME
#     else:
#         await update.message.reply_text('You are not authorized to use this command.')
#         return ConversationHandler.END
#
#
# async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     context.user_data['username'] = update.message.text
#     await update.message.reply_text('Please enter the amount of USDT to add to the user\'s balance:')
#     return AMOUNT
#
#
# async def receive_amount_to_increase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     username = context.user_data.get('username')
#     try:
#         amount = float(update.message.text)
#         user = User.get_user_by_username(username)
#         if user:
#             current_balance = user.get_balance()
#             new_balance = current_balance + amount
#             user.update_balance(new_balance)
#             await update.message.reply_text(
#                 f'Increased balance of user {username} by {amount} USDT. New balance: {new_balance} USDT')
#             logger.info(f"Increased balance of user {username} by {amount} USDT")
#         else:
#             await update.message.reply_text(f'User with username {username} not found.')
#             logger.warning(f"Attempted to increase balance for non-existing username {username}.")
#     except ValueError:
#         await update.message.reply_text('Invalid amount. Please enter a numeric value.')
#         logger.error("Invalid amount entered by admin.")
#
#     return ConversationHandler.END
# def create_table():
#     conn = sqlite3.connect('employees.db')
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS employees
#                  (telegram_id INTEGER PRIMARY KEY, username TEXT, balance REAL)''')
#     conn.commit()
#     conn.close()
#
# def main() -> None:
#     """Run the bot."""
#     create_table()
#     # We use persistence to demonstrate how buttons can still work after the bot was restarted
#     persistence = PicklePersistence(filepath="callbackdatabot")
#     # Create the Application and pass it your bot's token.
#     application = (
#         Application.builder()
#         .token(TELEGRAM_BOT_TOKEN)
#         .persistence(persistence)
#         .arbitrary_callback_data(True)
#         .build()
#     )
#
#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(CommandHandler('check_balance', check_balance))
#     conv_handler_increase = ConversationHandler(
#         entry_points=[CommandHandler('increase_balance', increase_balance)],
#         states={
#             USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_username)],
#             AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount_to_increase)],
#         },
#         fallbacks=[CommandHandler('cancel', cancel)],
#     )
#     application.add_handler(conv_handler_increase)
#
#     #application.add_handler(CommandHandler('withdraw', withdraw))
#     conv_handler_withdraw = ConversationHandler(
#         entry_points=[CommandHandler('withdraw', withdraw_start)],
#         states={
#             ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_wallet_address)],
#             AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount_to_withdraw)],
#         },
#         fallbacks=[CommandHandler('cancel', cancel)],
#     )
#     application.add_handler(conv_handler_withdraw)
#
#     # Run the bot until the user presses Ctrl-C
#     application.run_polling(allowed_updates=Update.ALL_TYPES)
#
#
# if __name__ == '__main__':
#     main()
#     # while True:
#     #     try:
#     #         asyncio.run(run_application())
#     #     except TimedOut:
#     #         logger.warning("Connection timed out. Retrying in 5 seconds...")
#     #         time.sleep(5)
