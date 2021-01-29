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
                     reply_markup=Keyboards.get_inline_tasks(list_), parse_mode='Markdown')
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
        cur_user.set_step(3, step_info=list_.get_json)
        bot.send_message(message.chat.id, MESSAGE.cant_get_list, reply_markup=Keyboards.get_main_menu())
    else:
        list_.add_task(Task(text=task_name))
        bot.send_message(message.chat.id, MESSAGE.task_added, reply_markup=Keyboards.get_inline_tasks(list_))


@Handler.request_decorator
@bot.message_handler(func=lambda m: Handler.get_user_step(m) == 4)
@Handler.get_current_user
def change_list_name_handler(message, cur_user: User):
    new_list_name = message.text
    list_id = cur_user.step_info['id']
    list_ = List.get_list(list_id)
    list_.change_name(new_list_name)
    bot.send_message(message.chat.id, MESSAGE.list_name_edited(new_list_name),
                     reply_markup=Keyboards.get_inline_tasks(list_), parse_mode='Markdown')
    cur_user.set_step(3, step_info=list_.get_json)


@Handler.request_decorator
@bot.callback_query_handler(func=lambda call: call_parser(call, type='task'))
def callback_inline(call):
    '''
    Изменяет статус задачи и обновляет inline список задач
    '''
    if call.message:
        call.info = json.loads(call.data)  # parse str to dict
        task = Task.get_task(task_id=call.info['id'])
        list_ = List.get_list(list_id=call.info['list_id'])
        if not task:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=MESSAGE.task_error,
                                  reply_markup=Keyboards.get_inline_tasks(list_))
        else:
            task.change_status()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=MESSAGE.list_selected(list_.name),
                                  reply_markup=Keyboards.get_inline_tasks(list_), parse_mode='Markdown')


@Handler.request_decorator
@bot.callback_query_handler(func=lambda call: call_parser(call, action='select list'))
@Handler.get_current_user_callback
def callback_inline(call, cur_user):
    if call.message:
        list_ = List.get_list(list_id=call.info['id'])
        cur_user.set_step(3, step_info=list_.get_json)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=MESSAGE.task_list,
                              reply_markup=Keyboards.get_inline_tasks(list_))


@Handler.request_decorator
@bot.callback_query_handler(func=lambda call: call_parser(call, action='main menu'))
@Handler.get_current_user_callback
def callback_inline(call, cur_user):
    if call.message:
        bot.send_message(call.message.chat.id, MESSAGE.main_menu, reply_markup=Keyboards.get_inline_list(cur_user))
        cur_user.set_step(1)


@Handler.request_decorator
@bot.callback_query_handler(func=lambda call: call_parser(call, action='edit list'))
@Handler.get_current_user_callback
def callback_inline(call, cur_user):
    if call.message:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=MESSAGE.list_menu,
                              reply_markup=Keyboards.get_inline_edit_list(List.get_list(list_id=call.info['list_id'])))


@Handler.request_decorator
@bot.callback_query_handler(func=lambda call: call_parser(call, action='change list name'))
@Handler.get_current_user_callback
def callback_inline(call, cur_user: User):
    if call.message:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=MESSAGE.edit_list_name, reply_markup=Keyboards.back())
        call.info.update({'prev_step': cur_user.step.step})
        cur_user.set_step(4, step_info=json.dumps(call.info))


@Handler.request_decorator
@bot.callback_query_handler(func=lambda call: call_parser(call, action='delete list'))
@Handler.get_current_user_callback
def callback_inline(call, cur_user: User):
    if call.message:
        list_ = List.get_list(list_id=call.info['id'])
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=MESSAGE.delete_list(list_.name), reply_markup=Keyboards.sure_delete(list_),
                              parse_mode='Markdown')


@Handler.request_decorator
@bot.callback_query_handler(func=lambda call: call_parser(call, action='sure delete list'))
@Handler.get_current_user_callback
def callback_inline(call, cur_user: User):
    if call.message:
        list_ = List.get_list(list_id=call.info['id'])
        name = list_.name
        current_session.delete(list_)
        current_session.commit()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=MESSAGE.sure_delete_list(name), reply_markup=Keyboards.get_main_menu(),
                              parse_mode='Markdown')
        cur_user.set_step(1)


bot.polling()
