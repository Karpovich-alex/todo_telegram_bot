import json
from database import User, List, Task
import telebot as t


class MESSAGE:
    cant_create_list = "Мы не смогли создать ваш список, попробуйте еще раз. Используйте уникальные имена для каждого списка"
    cant_get_list = "Не получилось добавить задачу в список :("
    task_added = "Задача добавлена!"
    task_error = "Произошла ошибка, попробуйте еще раз."
    task_list = "Вот список ваших задач:"
    main_menu = "Главное меню. Вот все ваши списки" + "\n чтобы добавить список просто напишите его название 👇"
    edit_list_name = "Введите измененое название списка"
    how_to_add_task = "чтобы добавить задачу просто напишите ее 👇"
    list_menu = "Выберите действия"

    @classmethod
    def list_created(cls, list_name):
        return f"Поздравляю вы создали список *{list_name}*. \n" + MESSAGE.how_to_add_task

    @classmethod
    def list_selected(cls, list_name):
        return f"Вот задачи из списка *{list_name}*" + "\n" + MESSAGE.how_to_add_task

    @classmethod
    def list_name_edited(cls, list_name):
        return f"Название списка изменено. Новое название: *{list_name}*" + "\n" + MESSAGE.how_to_add_task

    @classmethod
    def delete_list(cls, list_name):
        return f"Вы точно хотите удалить *{list_name}* ?"

    @classmethod
    def sure_delete_list(cls, list_name):
        return f"Вы удалили {list_name} !"


class Keyboards:
    @classmethod
    def get_inline_list(cls, cur_user: User) -> t.types.InlineKeyboardMarkup:
        keyboard = t.types.InlineKeyboardMarkup()
        for list_ in sorted(cur_user.lists, key=lambda lis: lis.id):
            callback_button = t.types.InlineKeyboardButton(text=list_.name,
                                                           callback_data=list_.get_custom_json(action='select list'))
            keyboard.add(callback_button)
        return keyboard

    @classmethod
    def get_inline_tasks(cls, list_: List):
        keyboard = t.types.InlineKeyboardMarkup()
        if list_.tasks:
            for task in sorted(list_.tasks, key=lambda t: t.id):
                task: Task
                callback_button = t.types.InlineKeyboardButton(text=task.inline_text,
                                                               callback_data=task.get_json.addinfo(
                                                                   {'action': 'selected'}).tostr())
                keyboard.add(callback_button)
        callback_button = t.types.InlineKeyboardButton(text='Изменить настройки списка',
                                                       callback_data=list_.get_json.addinfo({'action': 'edit'}).tostr())
        # callback_data=json.dumps(
        #             {"action": "edit list", "list_id": list_.id, "type": "action"})
        keyboard.add(callback_button)
        callback_button = t.types.InlineKeyboardButton(text='Выйти в главное меню',
                                                       callback_data=json.dumps({'action': 'menu'}))
        keyboard.add(callback_button)
        return keyboard

    @classmethod
    def get_inline_edit_list(cls, list_: List):
        keyboard = t.types.InlineKeyboardMarkup()
        b1 = t.types.InlineKeyboardButton(text="Изменить название",
                                          callback_data=list_.get_json.addinfo({'action': {'edit': 'name'}}).tostr())
        b2 = t.types.InlineKeyboardButton(text="Удалить список",
                                          callback_data=list_.get_json.addinfo({'action': 'delete'}).tostr())
        keyboard.add(b1, b2)
        return keyboard

    @classmethod
    def get_main_menu(cls):
        keyboard = t.types.InlineKeyboardMarkup()
        callback_button = t.types.InlineKeyboardButton(text='Показать все списки',
                                                       callback_data=json.dumps({'action': 'menu'}))
        keyboard.add(callback_button)
        return keyboard

    @classmethod
    def back(cls):
        keyboard = t.types.InlineKeyboardMarkup()
        callback_button = t.types.InlineKeyboardButton(text='Показать все списки',
                                                       callback_data=json.dumps({'action': 'menu'}))
        keyboard.add(callback_button)
        return keyboard

    @classmethod
    def sure_delete(cls, obj):
        keyboard = t.types.InlineKeyboardMarkup()
        b1 = t.types.InlineKeyboardButton(text='Удалить🗑️',
                                          callback_data=obj.get_json.addinfo({'action': 'delete'}).tostr())
        b2 = t.types.InlineKeyboardButton(text='Меню',
                                          callback_data=json.dumps({'action': 'menu'}))
        keyboard.row(b2, b1)
        return keyboard
