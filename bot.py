#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,  CallbackQueryHandler, BaseFilter
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import DataBase as DB


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
db = DB.DataBase('root','localhost','lezioni_db','')

selected_teaching = ''

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Lista comandi:\n- /listall: ritorna una lista di tutti gli insegnamenti')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def send_message(update, context):
    update.message.reply_text("asdasd")


def show_teachings_list(update, context):
    text = db.list_teachings()
    update.message.reply_text(text)


def show_teaching_info(update, context):
    if len(context.args) == 1:
        text = db.show_teaching_info(context.args[0])
        update.message.reply_text(text)
    elif len(context.args) == 0:
        update.message.reply_text(cdl_menu_message(), reply_markup=cdl_menu_keyboard())
    else:
        update.message.reply_text("Errore parametri")


def show_lessons(update, context):
    if len(context.args) == 1:
        text = db.get_lessons(context.args[0])
        update.message.reply_text(text)


#############################GUI_STUFF#############################

def cdl_menu(update, context):
    global selected_teaching
    if ("cdl" in update.callback_query.data):
        string = update.callback_query.data
        splitted = string.split("-")
        selected_teaching = splitted[1]
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=teaching_menu_message(), reply_markup=teaching_menu_keyboard())
    else:
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=cdl_menu_message(), reply_markup=cdl_menu_keyboard())


def cdl_menu_keyboard():
    cdl_names= db.get_cdl_list()
    keyboard = []
    for itm in cdl_names:
        keyboard.append([InlineKeyboardButton(itm, callback_data="cdl-"+str(itm))])
    return InlineKeyboardMarkup(keyboard)


def cdl_menu_message():
    return "Seleziona corso di laurea:"


def teaching_menu(update, context):
    if ("teaching" in update.callback_query.data):
        splitted = update.callback_query.data.split("-")
        text = db.show_teaching_info(splitted[1])
        query = update.callback_query
        query.answer()
        query.edit_message_text(text)
    else:
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=teaching_menu_message(), reply_markup=teaching_menu_keyboard())


def teaching_menu_keyboard():
    teachings_names, teachings_ids = db.get_cdl_teachings(selected_teaching)
    keyboard = []
    print(teachings_names, teachings_ids)
    for idx in range(len(teachings_names)):
        keyboard.append([InlineKeyboardButton(teachings_names[idx], callback_data='teaching-'+str(teachings_ids[idx]))])
    return InlineKeyboardMarkup(keyboard)


def teaching_menu_message():
    return "Seleziona insegnamento:"



#############################GUI_STUFF#############################



def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("token", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("listall", show_teachings_list))
    dp.add_handler(CommandHandler("info", show_teaching_info, pass_args=True))
    dp.add_handler(CommandHandler("lesson", show_lessons, pass_args=True))

    updater.dispatcher.add_handler(CallbackQueryHandler(cdl_menu, pattern='cdl'))
    updater.dispatcher.add_handler(CallbackQueryHandler(teaching_menu, pattern='teaching'))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()