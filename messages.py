import json
from database import User, List
import telebot as t


class MESSAGE:
    cant_create_list = "Мы не смогли создать ваш список, попробуйте еще раз. Используйте уникальные имена для каждого списка"
    cant_get_list = "Не получилось добавить задачу в список :("
    task_added = "Задача добавлена!"
    task_error = "Произошла ошибка, попробуйте еще раз."
    task_list = "Вот список ваших задач:"
    main_menu = "Главное меню. Вот все ваши списки"

    @classmethod
    def list_created(cls, list_name):
        return f"Поздравляю вы создали список <b>{list_name}</b>. \nЧтобы добавить задачу просто отправьте ее текст"

    @classmethod
    def list_selected(cls, list_name):
        return f"Вот задачи из списка {list_name}"


class Keyboards:
    @classmethod
    def get_inline_list(cls, cur_user: User) -> t.types.InlineKeyboardMarkup:
        keyboard = t.types.InlineKeyboardMarkup()
        for list_ in sorted(cur_user.lists, key=lambda lis: lis.id):
            callback_button = t.types.InlineKeyboardButton(text=list_.name, callback_data=list_.get_json)
            keyboard.add(callback_button)
        return keyboard

    @classmethod
    def get_inline_tasks(cls, list_: List):
        keyboard = t.types.InlineKeyboardMarkup()
        if list_.tasks:
            for task in sorted(list_.tasks, key=lambda t: t.id):
                callback_button = t.types.InlineKeyboardButton(text=task.inline_text, callback_data=task.get_json)
                keyboard.add(callback_button)
        callback_button = t.types.InlineKeyboardButton(text='Изменить настройки списка', callback_data=json.dumps(
            {"action": "edit list", "list_id": list_.id, "type": "action"}))
        keyboard.add(callback_button)
        callback_button = t.types.InlineKeyboardButton(text='Выйти в главное меню',
                                                       callback_data=json.dumps({'action': 'main menu'}))
        keyboard.add(callback_button)
        return keyboard

    @classmethod
    def get_inline_edit_list(cls, list_: List):
        pass

    @classmethod
    def get_main_menu(cls):
        keyboard = t.types.InlineKeyboardMarkup()
        callback_button = t.types.InlineKeyboardButton(text='Показать все списки',
                                                       callback_data=json.dumps({'action': 'main menu'}))
        keyboard.add(callback_button)
        return keyboard


def call_parser(call, **kwargs):
    call_data: dict = json.loads(call.data)
    for k, v in kwargs.items():
        if k not in call_data or call_data.get(k) != v:
            return False
    return True
