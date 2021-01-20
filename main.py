from typing import Tuple, Callable, Union
import telebot

from config import Config
from database import User, Task, List, current_session, init_db
from messages import MESSAGE, Keyboards
from utils import Handler

bot = telebot.TeleBot(Config.bot_api, parse_mode=None)
init_db()


@bot.message_handler(commands=['start'])
@Handler.request_decorator
def send_welcome(message):
    # markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    # itembtn1 = telebot.types.KeyboardButton('/add')
    # itembtn2 = telebot.types.KeyboardButton('/view')
    # markup.add(itembtn1, itembtn2)
    User.get_user(message=message)
    bot.send_message(message.chat.id, "Здравствуйте. Давайте для начала создадим список!")
    bot.send_message(message.chat.id, "Введите название списка:")
    # print(message)

#
# # handle if user step==1
# @Handler.get_current_user
# @bot.message_handler(func=lambda m: Handler.get_user_step(m) == 1)
# @Handler.request_decorator
# def list_name_handler(message, cur_user: User):
#     list_name = message.text
#     _list = List(name=list_name, users=cur_user)
#     if cur_user.create_list(_list):
#         bot.send_message(message.chat.id, MESSAGE.list_created(list_name),
#                          reply_markup=Keyboards.get_inline_tasks(_list))
#         cur_user.step = 3
#         cur_user.step.info = _list.get_json
#     else:
#         bot.send_message(message.chat.id, MESSAGE.cant_create_list, reply_markup=Keyboards.get_main_menu())
#         cur_user.step = 0
#
#
# @Handler.get_current_user
# @bot.message_handler(func=lambda m: Handler.get_user_step(m) == 3)
# @Handler.request_decorator
# def task_name_handler(message, cur_user: User):
#     task_name = message.text
#     if cur_user.step.info['type'] != 'List':
#         raise AttributeError('Last action was not choosing list')
#     list_id = cur_user.step.info['id']
#     _list = List.get_list(list_id)
#     if not _list:
#         cur_user.step = 3
#         bot.send_message(message.chat.id, MESSAGE.cant_get_list, reply_markup=Keyboards.get_main_menu())
#     else:
#         _list.add_task(Task(text=task_name))
#         bot.send_message(message.chat.id, MESSAGE.task_added, reply_markup=Keyboards.get_inline_tasks(_list))
#
#
# @bot.callback_query_handler(func=lambda call: call.data['type'] == 'task')
# @Handler.request_decorator
# def callback_inline(call):
#     # Если сообщение из чата с ботом
#     if call.message:
#         task = Task.get_task(task_id=call.data['id'])
#         if not task:
#             bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                   text=MESSAGE.task_error,
#                                   reply_markup=Keyboards.get_inline_tasks(List.get_list(list_id=call.data['task_id'])))
#         else:
#             task.change_status()
#             bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                   text=MESSAGE.task_list, reply_markup=Keyboards.get_inline_tasks(
#                     List.get_list(list_id=call.data['task_id'])))
#
#
# @bot.callback_query_handler(func=lambda call: call.data['type'] == 'list')
# @Handler.request_decorator
# def callback_inline(call):
#     # Если сообщение из чата с ботом
#     if call.message:
#         _list = List.get_list(list_id=call.data['id'])
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                               text=MESSAGE.task_error,
#                               reply_markup=Keyboards.get_inline_tasks(List.get_list(list_id=call.data['id'])))
#
#
# @bot.callback_query_handler(func=lambda call: call.data['action'] == 'edit list')
# @Handler.request_decorator
# def callback_inline(call):
#     if call.message:
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                               text=MESSAGE.task_error,
#                               reply_markup=Keyboards.get_inline_edit_list(List.get_list(list_id=call.data['list_id'])))

print('here')
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
