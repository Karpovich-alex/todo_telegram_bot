import json
from database import User, List
import telebot as t


class MESSAGE:
    cant_create_list = "Мы не смогли создать ваш список, попробуйте еще раз. Используйте уникальные имена для каждого списка"
    cant_get_list = "Не получилось добавить задачу в список :("
    task_added = "Задача добавлена!"
    task_error = "Произошла ошибка, попробуйте еще раз."
    task_list = "Вот список ваших задач:"

    @classmethod
    def list_created(cls, list_name):
        return f"Поздравляю вы создали список {list_name}. \nЧтобы добавить задачу просто отправьте ее текст"


class Keyboards:
    @classmethod
    def get_inline_list(cls, cur_user: User) -> t.types.InlineKeyboardMarkup:
        keyboard = t.types.InlineKeyboardMarkup()
        for _list in cur_user.lists:
            callback_button = t.types.InlineKeyboardButton(text=_list.name, callback_data=_list.get_json())
            keyboard.add(callback_button)
        return keyboard

    @classmethod
    def get_inline_tasks(cls, _list: List):
        keyboard = t.types.InlineKeyboardMarkup()
        for task in _list.tasks:
            callback_button = t.types.InlineKeyboardButton(text=task.inline_text, callback_data=task.get_json)
            keyboard.add(callback_button)
        callback_button = t.types.InlineKeyboardButton(text='Изменить список', callback_data=json.dumps({'action': 'edit list', "list_id": _list.id}))
        keyboard.add(callback_button)
        return keyboard

    @classmethod
    def get_inline_edit_list(cls, _list: List):
        pass


    @classmethod
    def get_main_menu(cls):
        keyboard = t.types.InlineKeyboardMarkup()
        callback_button = t.types.InlineKeyboardButton(text='Показать все списки', callback_data=json.dumps({'action':'main menu'}))
        keyboard.add(callback_button)
        return "Выберете команду на клавиатуре"
