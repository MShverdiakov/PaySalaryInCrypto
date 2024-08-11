import logging
import sqlite3

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from models import User
from services.tron_service import process_withdrawal
from config import logger, ADMIN_ID

USERNAME, AMOUNT, ADDRESS, APPROVE = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Create or update user in the database
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute('''
           INSERT INTO employees (telegram_id, username, balance)
           VALUES (?, ?, 0)
           ON CONFLICT(telegram_id) 
           DO UPDATE SET username = excluded.username
       ''', (user_id, username))
    conn.commit()
    conn.close()

    # Send welcome message and menu
    await update.message.reply_text('Welcome! Please choose an option from the menu below:',
                                    reply_markup=main_menu_keyboard())

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Please choose an option from the menu below:',
                                    reply_markup=main_menu_keyboard())

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Check Balance", callback_data='check_balance')],
        [InlineKeyboardButton("Withdraw", callback_data='withdraw')],
        [InlineKeyboardButton("Help", callback_data='help')],
    ]
    return InlineKeyboardMarkup(keyboard)

async def menu_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'check_balance':
        await check_balance(update, context)
    elif query.data == 'withdraw':
        await withdraw_start(update, context)
    elif query.data == 'help':
        await help_command(update, context)

async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        user_id = update.message.from_user.id
    elif update.callback_query:
        user_id = update.callback_query.from_user.id
    else:
        logger.error("Unable to retrieve user ID.")
        return

    user = User.get_user_by_telegram_id(user_id)
    if user:
        balance = user.get_balance()
        response_text = f'Your balance is: {balance} USDT'
    else:
        response_text = 'No balance found.'

    if update.message:
        await update.message.reply_text(response_text)
    elif update.callback_query:
        await update.callback_query.edit_message_text(response_text)


async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message:
        user_id = update.message.from_user.id
        logger.info(f"User {user_id} started withdrawal process.")
        await update.message.reply_text('Please enter your USDT wallet address:')
    elif update.callback_query:
        user_id = update.callback_query.from_user.id
        logger.info(f"User {user_id} started withdrawal process.")
        await update.callback_query.edit_message_text("Click /withdraw to start withdrawal")
    else:
        logger.error("Unable to withdraw")
        return

    return ADDRESS

async def receive_wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    employee_wallet_address = update.message.text

    try:
        # Validate wallet address
        context.user_data['wallet_address'] = employee_wallet_address
        await update.message.reply_text('Please enter the amount of USDT you want to withdraw:')
        return AMOUNT
    except ValueError as e:
        await update.message.reply_text(str(e) + " Please enter a valid USDT address.")
        return ADDRESS

async def receive_amount_to_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
        else:
            logger.error("Unable to retrieve user ID.")

        user = User.get_user_by_telegram_id(user_id)
        balance = user.get_balance()
        usdt_amount = float(update.message.text)
        if usdt_amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        if usdt_amount > balance:
            raise ValueError(f"You have only {balance} USDT on your balance")

        context.user_data['amount'] = usdt_amount
        if update.message:
            await update.message.reply_text(
                f"Confirm withdrawal of {usdt_amount} USDT to {context.user_data['wallet_address']}?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Yes", callback_data='approve_withdrawal')],
                    [InlineKeyboardButton("No", callback_data='cancel')]
                ]))
        return APPROVE
    except ValueError:
        await update.message.reply_text("Invalid amount. Please enter a numeric value.")
        return AMOUNT

async def approve_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user_id = query.from_user.id
    user = User.get_user_by_telegram_id(user_id)
    amount = context.user_data['amount']
    wallet_address = context.user_data['wallet_address']

    try:
        result = process_withdrawal(wallet_address, amount)
        if result:
            new_balance = user.get_balance() - amount
            user.update_balance(new_balance)
            await query.edit_message_text(f"Withdrawal of {amount} USDT successful. New balance: {new_balance} USDT")
        else:
            await query.edit_message_text("Withdrawal failed. Please try again later.")
    except Exception as e:
        await query.edit_message_text(f"An error occurred: {str(e)}")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        if update.message:
            await update.message.reply_text('Withdrawal process cancelled.')
            logger.info(f"User {update.message.from_user.id} cancelled the withdrawal process.")
        else:
            logger.warning("No message found in update during cancellation.")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error during cancellation: {str(e)}")
        if update.message:
            await update.message.reply_text('An error occurred while cancelling the process.')
        return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Here are the available commands:\n"
        "/start - Start the bot and register your username.\n"
        "/menu - calls a standard menu.\n"
        "/check_balance - Check your current USDT balance.\n"
        "/withdraw - Initiate a withdrawal process.\n"
        "/cancel - Cancel any ongoing operations.\n"
        "/help - Show this help message."
    )
    if update.message:
        await update.message.reply_text(help_text)
    elif update.callback_query:
        await update.callback_query.edit_message_text(help_text)

async def increase_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.from_user.id == ADMIN_ID:
        await update.message.reply_text('Please enter the username of the employee whose balance you want to increase:')
        return USERNAME
    else:
        await update.message.reply_text('You are not authorized to use this command.')
        return ConversationHandler.END

async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['username'] = update.message.text
    await update.message.reply_text('Please enter the amount of USDT to add to the user\'s balance:')
    return AMOUNT

async def receive_amount_to_increase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = context.user_data.get('username')
    try:
        amount = float(update.message.text)
        user = User.get_user_by_username(username)
        if user:
            current_balance = user.get_balance()
            new_balance = current_balance + amount
            user.update_balance(new_balance)
            await update.message.reply_text(
                f'Increased balance of user {username} by {amount} USDT. New balance: {new_balance} USDT')
            logger.info(f"Increased balance of user {username} by {amount} USDT")
        else:
            await update.message.reply_text(f'User with username {username} not found.')
            logger.warning(f"Attempted to increase balance for non-existing username {username}.")
    except ValueError:
        await update.message.reply_text('Invalid amount. Please enter a numeric value.')
        logger.error("Invalid amount entered by admin.")

    return ConversationHandler.END