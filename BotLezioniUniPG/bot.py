#!/usr/bin/env python

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,  CallbackQueryHandler, BaseFilter
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from DataBase import DataBase


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

selected_cdl = ""
inserted_keyword = ""
professor_name = ""


def start_command(update, context):
    update.message.reply_text("Usa il comando /help per visualizzare la lista dei comandi.")


def help_command(update, context):
    update.message.reply_text(open('help').read())


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def list_command(update, context):
    update.message.reply_text(cdl_menu_message(), reply_markup=cdl_list_menu_keyboard())


def info_command(update, context):
    if len(context.args) == 1:
        if check_if_int(context.args[0]):
            db = DataBase.get_instance()
            text = db.show_teaching_info(context.args[0])
            update.message.reply_text(text, disable_web_page_preview=True)
        else:
            update.message.reply_text("Errore: il parametro deve essere un numero intero.")
    elif len(context.args) == 0:
        update.message.reply_text(cdl_menu_message(), reply_markup=cdl_menu_keyboard())
    else:
        update.message.reply_text("Errore: inserire uno o nessun parametro.")


def lesson_command(update, context):
    if len(context.args) == 1:
        if check_if_int(context.args[0]):
            db = DataBase.get_instance()
            text = db.get_lessons(context.args[0])
            update.message.reply_text(text)
        else:
            update.message.reply_text("Errore: il parametro deve essere un numero intero.")
    elif len(context.args) == 0:
        update.message.reply_text(cdl_menu_message(), reply_markup=lesson_menu_keyboard())
    else:
        update.message.reply_text("Errore: inserire uno o nessun parametro.")


def search_command(update, context):
    global inserted_keyword
    if len(context.args) > 0:
        keyword = ""
        for itm in context.args:
            keyword += str(itm) + " "
        keyword = keyword[:-1]
        if len(keyword) <= 500:
            inserted_keyword = keyword
            update.message.reply_text(cdl_menu_message(), reply_markup=cdl_search_menu_keyboard())
        else:
            update.message.reply_text("Errore: il parametro non deve contenere più di 500 caratteri.")
    else:
        update.message.reply_text("Errore: nessun parametro inserito.")


def prof_command(update, context):
    global professor_name
    if len(context.args) > 0:
        name = ""
        for itm in context.args:
            name += str(itm) + " "
        name = name[:-1]
        if len(name) <= 500:
            professor_name = name
            update.message.reply_text(cdl_menu_message(), reply_markup=cdl_search_professor_keyboard())
        else:
            update.message.reply_text("Errore: il parametro non deve contenere più di 500 caratteri.")
    else:
        update.message.reply_text("Errore: nessun parametro inserito.")


def check_if_int(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


def unknow_command(update, context):
    known = ['/help', '/list', '/info', '/lesson', '/search', '/prof', '/start']
    command = update.message.text.split(' ')[0]
    if command not in known:
        update.message.reply_text("Comando non riconosciuto. Provare comando /help per vedere la lista dei comandi.")


def cdl_menu(update, context):
    global selected_cdl
    global professor_name
    if "cdl_info" in update.callback_query.data:
        string = update.callback_query.data
        splitted = string.split("-")
        selected_cdl = splitted[1]
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=teaching_menu_message(), reply_markup=teaching_menu_keyboard())
    elif "cdl_list" in update.callback_query.data:
        db = DataBase.get_instance()
        string = update.callback_query.data
        splitted = string.split("-")
        text = db.list_teachings(splitted[1])
        query = update.callback_query
        query.answer()
        query.edit_message_text(text, disable_web_page_preview=True)
    elif "cdl_search" in update.callback_query.data:
        db = DataBase.get_instance()
        string = update.callback_query.data
        splitted = string.split("-")
        text = db.search_by_keyword(inserted_keyword, splitted[1])
        if not text:
            text = "Non è stato trovato nessun insegnamento corrispondente al parametro inserito"
        query = update.callback_query
        query.answer()
        query.edit_message_text(text, disable_web_page_preview=True)
    elif "cdl_lesson" in update.callback_query.data:
        string = update.callback_query.data
        splitted = string.split("-")
        selected_cdl = splitted[1]
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=teaching_menu_message(), reply_markup=teaching_lesson_menu_keyboard())
    elif "cdl_prof" in update.callback_query.data:
        db = DataBase.get_instance()
        string = update.callback_query.data
        splitted = string.split("-")
        text = db.search_by_name(professor_name, splitted[1])
        if not text:
            text = "Non è stato trovato nessun insegnamento corrispondente al parametro inserito"
        query = update.callback_query
        query.answer()
        query.edit_message_text(text, disable_web_page_preview=True)



def cdl_menu_keyboard():
    db = DataBase.get_instance()
    cdl_names= db.get_cdl_list()
    keyboard = []
    for itm in cdl_names:
        keyboard.append([InlineKeyboardButton(itm, callback_data="cdl_info-"+str(itm))])
    return InlineKeyboardMarkup(keyboard)


def cdl_menu_message():
    return "Seleziona corso di laurea:"


def teaching_menu(update, context):
    if "teaching_info" in update.callback_query.data:
        db = DataBase.get_instance()
        splitted = update.callback_query.data.split("-")
        text = db.show_teaching_info(splitted[1])
        query = update.callback_query
        query.answer()
        query.edit_message_text(text, disable_web_page_preview=True)
    elif "teaching_lessons" in update.callback_query.data:
        db = DataBase.get_instance()
        splitted = update.callback_query.data.split("-")
        text = db.get_lessons(splitted[1])
        query = update.callback_query
        query.answer()
        query.edit_message_text(text, disable_web_page_preview=True)


def teaching_menu_keyboard():
    db = DataBase.get_instance()
    teachings_names, teachings_ids = db.get_cdl_teachings(selected_cdl)
    keyboard = []
    for idx in range(len(teachings_names)):
        keyboard.append([InlineKeyboardButton(teachings_names[idx], callback_data='teaching_info-'+str(teachings_ids[idx]))])
    return InlineKeyboardMarkup(keyboard)


def teaching_lesson_menu_keyboard():
    db = DataBase.get_instance()
    teachings_names, teachings_ids = db.get_cdl_teachings(selected_cdl)
    keyboard = []
    for idx in range(len(teachings_names)):
        keyboard.append([InlineKeyboardButton(teachings_names[idx], callback_data='teaching_lessons-'+str(teachings_ids[idx]))])
    return InlineKeyboardMarkup(keyboard)


def teaching_menu_message():
    return "Seleziona insegnamento:"


def cdl_list_menu_keyboard():
    db = DataBase.get_instance()
    cdl_names= db.get_cdl_list()
    keyboard = []
    for itm in cdl_names:
        keyboard.append([InlineKeyboardButton(itm, callback_data="cdl_list-"+str(itm))])
    return InlineKeyboardMarkup(keyboard)


def cdl_search_menu_keyboard():
    db = DataBase.get_instance()
    cdl_names= db.get_cdl_list()
    keyboard = [[InlineKeyboardButton("Tutti", callback_data="cdl_search-all")]]
    for itm in cdl_names:
        keyboard.append([InlineKeyboardButton(itm, callback_data="cdl_search-"+str(itm))])
    return InlineKeyboardMarkup(keyboard)


def lesson_menu_keyboard():
    db = DataBase.get_instance()
    cdl_names= db.get_cdl_list()
    keyboard = []
    for itm in cdl_names:
        keyboard.append([InlineKeyboardButton(itm, callback_data="cdl_lesson-"+str(itm))])
    return InlineKeyboardMarkup(keyboard)


def cdl_search_professor_keyboard():
    db = DataBase.get_instance()
    cdl_names= db.get_cdl_list()
    keyboard = [[InlineKeyboardButton("Tutti", callback_data="cdl_prof-all")]]
    for itm in cdl_names:
        keyboard.append([InlineKeyboardButton(itm, callback_data="cdl_prof-"+str(itm))])
    return InlineKeyboardMarkup(keyboard)


def main():


    updater = Updater(open('token').read(), use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("list", list_command))
    dp.add_handler(CommandHandler("info", info_command, pass_args=True))
    dp.add_handler(CommandHandler("lesson", lesson_command, pass_args=True))
    dp.add_handler(CommandHandler("search", search_command, pass_args=True))
    dp.add_handler(CommandHandler("prof", prof_command, pass_args=True))
    dp.add_handler(MessageHandler(Filters.text, unknow_command))
    dp.add_handler(MessageHandler(Filters.command, unknow_command))

    updater.dispatcher.add_handler(CallbackQueryHandler(cdl_menu, pattern='cdl'))
    updater.dispatcher.add_handler(CallbackQueryHandler(teaching_menu, pattern='teaching'))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()