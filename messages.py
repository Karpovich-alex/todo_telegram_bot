from database import User, List
import telebot as t


class MESSAGE:
    cant_create_list = "Мы не смогли создать ваш список, попробуйте еще раз. Используйте уникальные имена для каждого списка"

    @classmethod
    def list_created(cls, list_name):
        return f"Поздравляю вы создали список {list_name}"


class Keyboards:
    @classmethod
    def get_inline_list(cls, cur_user: User) -> t.types.InlineKeyboardMarkup:
        keyboard = t.types.InlineKeyboardMarkup()
        for _list in cur_user.lists:
            callback_button = t.types.InlineKeyboardButton(text=_list.name, callback_data=_list.get_json())
            keyboard.add(callback_button)
        return keyboard

    @classmethod
    def get_inline_tasks(cls, _list:List):
        keyboard = t.types.InlineKeyboardMarkup()
        for task in _list.tasks:
            callback_button = t.types.InlineKeyboardButton(text=task.text, callback_data=task.get_json())
            keyboard.add(callback_button)
        return keyboard

    @classmethod
    def get_main_menu(cls):
        return "Выберете команду на клавиатуре"

