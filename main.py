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


def get_inline_keyboard(user_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for t_text, t_callback in UserDb.get_all_tasks(tg_id=user_id):
        callback_button = telebot.types.InlineKeyboardButton(text=t_text, callback_data=t_callback)
        keyboard.add(callback_button)
    return keyboard


@bot.message_handler(commands=['view'])
def view_tasks(message):
    keyboard = get_inline_keyboard(message.from_user.id)
    bot.send_message(message.chat.id, "Вот ваши задачи", reply_markup=keyboard)


# В большинстве случаев целесообразно разбить этот хэндлер на несколько маленьких
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        if call.data[0] == "t":
            UserDb.edit_task(callback_data=call.data)
            keyboard = get_inline_keyboard(call.from_user.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Вот ваши задачи", reply_markup=keyboard)
        else:
            keyboard = get_inline_keyboard(call.from_user.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Вот ваши задачи", reply_markup=keyboard)


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
