from typing import Tuple, Callable, Union
import telebot

from config import Config
from database import User, Task, current_session
from messages import MESSAGE, Keyboards

bot = telebot.TeleBot(Config.bot_api, parse_mode=None)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('/add')
    itembtn2 = telebot.types.KeyboardButton('/view')
    markup.add(itembtn1, itembtn2)
    User.get_user(message=message)
    bot.send_message(message.chat.id, "Здравствуйте. Давайте для начала создадим список!", reply_markup=markup)
    bot.send_message(message.chat.id, "Введите название списка:")
    # print(message)


def dec_get_current_user(f) -> Callable:
    def dec(*params, **kw) -> Tuple[telebot.types.Message, User]:
        message: telebot.types.Message = f(*params, **kw)
        return (message, get_current_user(message))

    return dec


def get_current_user(message: telebot.types.Message) -> User:
    return User.get_user(message=message)


def get_user_step(message: telebot.types.Message) -> int:
    return get_current_user(message).step


# handle if user step==1
@dec_get_current_user
@bot.message_handler(func=lambda m: get_user_step(m) == 1)
def list_name_handler(message, cur_user: User):
    list_name = message.text
    if User.create_list(list_name=list_name, user=cur_user):
        bot.send_message(message.chat.id, MESSAGE.list_created(list_name), reply_markup=Keyboards.get_list(cur_user))
        cur_user.step = 2
    else:
        bot.send_message(message.chat.id, MESSAGE.cant_create_list, reply_markup=Keyboards.get_main_menu())
        cur_user.step = 0

# @bot.message_handler(commands=['add'])
# def add_task(message):
#     markup = telebot.types.ForceReply(selective=False)
#     bot.reply_to(message, "Write task text", reply_markup=markup)
#
#
# def get_inline_keyboard(user_id):
#     keyboard = telebot.types.InlineKeyboardMarkup()
#     for t_text, t_callback in User.get_all_tasks(tg_id=user_id):
#         callback_button = telebot.types.InlineKeyboardButton(text=t_text, callback_data=t_callback)
#         keyboard.add(callback_button)
#     return keyboard
#
#
# @bot.message_handler(commands=['view'])
# def view_tasks(message):
#     keyboard = get_inline_keyboard(message.from_user.id)
#     bot.send_message(message.chat.id, "Вот ваши задачи", reply_markup=keyboard)
#
#
# # В большинстве случаев целесообразно разбить этот хэндлер на несколько маленьких
# @bot.callback_query_handler(func=lambda call: True)
# def callback_inline(call):
#     # Если сообщение из чата с ботом
#     if call.message:
#         if call.data[0] == "t":
#             User.edit_task(callback_data=call.data)
#             keyboard = get_inline_keyboard(call.from_user.id)
#             bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                   text="Вот ваши задачи", reply_markup=keyboard)
#         else:
#             keyboard = get_inline_keyboard(call.from_user.id)
#             bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                   text="Вот ваши задачи", reply_markup=keyboard)
#
#
# @bot.message_handler(content_types=['text'])
# def _add_task(message):
#     if message.reply_to_message:
#         User.add_task(text=message.text, tg_id=message.from_user.id)
#     markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
#     itembtn1 = telebot.types.KeyboardButton('/add')
#     itembtn2 = telebot.types.KeyboardButton('/view')
#     markup.add(itembtn1, itembtn2)
#     bot.reply_to(message, "Task added", reply_markup=markup)


bot.polling()
