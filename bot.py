#!/usr/bin/env python

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,  CallbackQueryHandler, BaseFilter
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from DataBase import DataBase


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
db =  DataBase.get_instance('root','localhost','lezioni_db','')

selected_teaching = ""
inserted_keyword = ""


def help(update, context):
    update.message.reply_text(open('help').read())


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def show_teachings_list(update, context):
    update.message.reply_text(cdl_menu_message(), reply_markup=cdl_list_menu_keyboard())


def show_teaching_info(update, context):
    if len(context.args) == 1:
        text = db.show_teaching_info(context.args[0])
        update.message.reply_text(text)
    elif len(context.args) == 0:
        update.message.reply_text(cdl_menu_message(), reply_markup=cdl_menu_keyboard())
    else:
        update.message.reply_text("Errore: inserire uno o zero parametri.")


def show_lessons(update, context):
    if len(context.args) == 1:
        text = db.get_lessons(context.args[0])
        update.message.reply_text(text)
    elif len(context.args) == 0:
        update.message.reply_text(cdl_menu_message(), reply_markup=lesson_menu_keyboard())
    else:
        update.message.reply_text("Errore: inserire uno o zero parametri.")


def search_teaching(update, context):
    global inserted_keyword
    if len(context.args) > 0:
        keyword = ""
        for itm in context.args:
            keyword += str(itm) + " "
        keyword = keyword[:-1]
        inserted_keyword = keyword
        update.message.reply_text(cdl_menu_message(), reply_markup=cdl_search_menu_keyboard())
    else:
        update.message.reply_text("Errore: nessun parametro inserito.")


#############################GUI_STUFF#############################

def cdl_menu(update, context):
    global selected_teaching
    if "cdl_info" in update.callback_query.data:
        string = update.callback_query.data
        splitted = string.split("-")
        selected_teaching = splitted[1]
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=teaching_menu_message(), reply_markup=teaching_menu_keyboard())
    elif "cdl_list" in update.callback_query.data:
        string = update.callback_query.data
        splitted = string.split("-")
        text = db.list_teachings(splitted[1])
        query = update.callback_query
        query.answer()
        query.edit_message_text(text)
    elif "cdl_search" in update.callback_query.data:
        string = update.callback_query.data
        splitted = string.split("-")
        text = db.search_by_keyword(inserted_keyword,splitted[1])
        if not text:
            text = "Nessun insgamento"
        query = update.callback_query
        query.answer()
        query.edit_message_text(text)
    elif "cdl_lesson" in update.callback_query.data:
        string = update.callback_query.data
        splitted = string.split("-")
        selected_teaching = splitted[1]
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=teaching_menu_message(), reply_markup=teaching_lesson_menu_keyboard())


def cdl_menu_keyboard():
    cdl_names= db.get_cdl_list()
    keyboard = []
    for itm in cdl_names:
        keyboard.append([InlineKeyboardButton(itm, callback_data="cdl_info-"+str(itm))])
    return InlineKeyboardMarkup(keyboard)


def cdl_menu_message():
    return "Seleziona corso di laurea:"


def teaching_menu(update, context):
    print(update.callback_query.data)
    if "teaching_info" in update.callback_query.data:
        splitted = update.callback_query.data.split("-")
        text = db.show_teaching_info(splitted[1])
        query = update.callback_query
        query.answer()
        query.edit_message_text(text)
    elif "teaching_lessons" in update.callback_query.data:
        splitted = update.callback_query.data.split("-")
        text = db.get_lessons(splitted[1])
        print(text)
        query = update.callback_query
        query.answer()
        query.edit_message_text(text)


def teaching_menu_keyboard():
    teachings_names, teachings_ids = db.get_cdl_teachings(selected_teaching)
    keyboard = []
    for idx in range(len(teachings_names)):
        keyboard.append([InlineKeyboardButton(teachings_names[idx], callback_data='teaching_info-'+str(teachings_ids[idx]))])
    return InlineKeyboardMarkup(keyboard)


def teaching_lesson_menu_keyboard():
    teachings_names, teachings_ids = db.get_cdl_teachings(selected_teaching)
    keyboard = []
    for idx in range(len(teachings_names)):
        keyboard.append([InlineKeyboardButton(teachings_names[idx], callback_data='teaching_lessons-'+str(teachings_ids[idx]))])
    return InlineKeyboardMarkup(keyboard)


def teaching_menu_message():
    return "Seleziona insegnamento:"


def cdl_list_menu_keyboard():
    cdl_names= db.get_cdl_list()
    keyboard = []
    for itm in cdl_names:
        keyboard.append([InlineKeyboardButton(itm, callback_data="cdl_list-"+str(itm))])
    return InlineKeyboardMarkup(keyboard)


def cdl_search_menu_keyboard():
    cdl_names= db.get_cdl_list()
    keyboard = [[InlineKeyboardButton("Tutti", callback_data="cdl_search-all")]]
    for itm in cdl_names:
        keyboard.append([InlineKeyboardButton(itm, callback_data="cdl_search-"+str(itm))])
    return InlineKeyboardMarkup(keyboard)


def lesson_menu_keyboard():
    cdl_names= db.get_cdl_list()
    keyboard = []
    for itm in cdl_names:
        keyboard.append([InlineKeyboardButton(itm, callback_data="cdl_lesson-"+str(itm))])
    return InlineKeyboardMarkup(keyboard)


#############################GUI_STUFF#############################


def main():


    updater = Updater("token", use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("list", show_teachings_list))
    dp.add_handler(CommandHandler("info", show_teaching_info, pass_args=True))
    dp.add_handler(CommandHandler("lesson", show_lessons, pass_args=True))
    dp.add_handler(CommandHandler("search", search_teaching, pass_args=True))

    updater.dispatcher.add_handler(CallbackQueryHandler(cdl_menu, pattern='cdl'))
    updater.dispatcher.add_handler(CallbackQueryHandler(teaching_menu, pattern='teaching'))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
