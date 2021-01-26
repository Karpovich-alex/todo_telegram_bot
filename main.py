from typing import Tuple, Callable, Union
import telebot
import json

from config import Config
from database import User, Task, List, current_session, init_db
from messages import MESSAGE, Keyboards, call_parser
from utils import Handler

bot = telebot.TeleBot(Config.bot_api, parse_mode=None)
init_db()


@Handler.request_decorator
@bot.message_handler(commands=['start'])
def send_welcome(message):
    u = User.get_user(message=message)
    bot.send_message(message.chat.id, "Здравствуйте. Давайте для начала создадим список!")
    bot.send_message(message.chat.id, "Введите название списка:")
    u.set_step(1)


# handle if user step==1

@Handler.request_decorator
@bot.message_handler(func=lambda m: Handler.get_user_step(m) == 1)
@Handler.get_current_user
def list_name_handler(message, cur_user: User):
    list_name = message.text
    list_ = List(name=list_name, users=cur_user)
    cur_user.create_list(list_)
    bot.send_message(message.chat.id, MESSAGE.list_created(list_name),
                     reply_markup=Keyboards.get_inline_tasks(list_))
    cur_user.set_step(3, step_info=list_.get_json)


@Handler.request_decorator
@bot.message_handler(func=lambda m: Handler.get_user_step(m) == 3)
@Handler.get_current_user
def task_name_handler(message, cur_user: User):
    task_name = message.text
    if cur_user.step_info['type'] != 'list':
        raise AttributeError('Last action was not choosing list')
    list_id = cur_user.step_info['id']
    list_ = List.get_list(list_id)
    if not list_:
        cur_user.set_step(3)
        bot.send_message(message.chat.id, MESSAGE.cant_get_list, reply_markup=Keyboards.get_main_menu())
    else:
        list_.add_task(Task(text=task_name))
        bot.send_message(message.chat.id, MESSAGE.task_added, reply_markup=Keyboards.get_inline_tasks(list_))


@Handler.request_decorator
@bot.callback_query_handler(func=lambda call: call_parser(call, type='task'))
def callback_inline(call):
    '''
    Изменяет статус задачи и обновляет inline список задач
    '''
    if call.message:
        call.message.info = json.loads(call.data)  # parse str to dict
        task = Task.get_task(task_id=call.message.info['id'])
        list_ = List.get_list(list_id=call.message.info['list_id'])
        if not task:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=MESSAGE.task_error,
                                  reply_markup=Keyboards.get_inline_tasks(list_))
        else:
            task.change_status()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=MESSAGE.task_list, reply_markup=Keyboards.get_inline_tasks(list_))


@Handler.request_decorator
@bot.callback_query_handler(func=lambda call: call_parser(call, type='list'))
def callback_inline(call):
    if call.message:
        list_ = List.get_list(list_id=json.loads(call.data)['id'])

        cur_user = User.get_user(message=call.message)
        cur_user.set_step(3, step_info=list_.get_json)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=MESSAGE.task_list,
                              reply_markup=Keyboards.get_inline_tasks(list_))


@Handler.request_decorator
@bot.callback_query_handler(
    func=lambda call: call_parser(call, action='main menu'))
def callback_inline(call):
    if call.message:
        cur_user = User.get_user(tg_id=call.from_user.id)
        bot.send_message(call.message.chat.id, MESSAGE.main_menu, reply_markup=Keyboards.get_inline_list(cur_user))
        cur_user.set_step(1)


@bot.callback_query_handler(func=lambda call: call_parser(call, action='edit list'))
@Handler.request_decorator
def callback_inline(call):
    if call.message:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=MESSAGE.task_error,
                              reply_markup=Keyboards.get_inline_edit_list(List.get_list(list_id=call.data['list_id'])))


bot.polling()
