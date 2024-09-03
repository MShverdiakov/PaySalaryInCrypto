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

