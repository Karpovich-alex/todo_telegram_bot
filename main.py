import telebot
from config import Config
import database

UserDb = database.UserDb

bot = telebot.TeleBot(Config.bot_api, parse_mode=None)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('/add')
    itembtn2 = telebot.types.KeyboardButton('/view')
    markup.add(itembtn1, itembtn2)
    UserDb.get_user(user=message.from_user)
    bot.send_message(message.chat.id, "Hi, how are you doing?", reply_markup=markup)
    # print(message)


@bot.message_handler(commands=['add'])
def add_task(message):
    markup = telebot.types.ForceReply(selective=False)
    bot.reply_to(message, "Write task text", reply_markup=markup)


@bot.message_handler(commands=['view'])
def view_tasks(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    url_button = telebot.types.InlineKeyboardButton(text="Перейти на Яндекс", url="https://ya.ru")
    tasks = UserDb.get_all_tasks(message.from_user.id)
    bot.send_message(message.chat.id, tasks)


@bot.message_handler(content_types=['text'])
def _add_task(message):
    if message.reply_to_message:
        UserDb.add_task(text=message.text, tg_id=message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('/add')
    itembtn2 = telebot.types.KeyboardButton('/view')
    markup.add(itembtn1, itembtn2)
    bot.reply_to(message, "Task added", reply_markup=markup)


bot.polling()
