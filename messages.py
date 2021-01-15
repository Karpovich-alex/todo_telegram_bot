from database import User
import telebot as t


class MESSAGE:
    cant_create_list = "Мы не смогли создать ваш список, попробуйте еще раз. Используйте уникальные имена для каждого списка"

    @classmethod
    def list_created(cls, list_name):
        return f"Поздравляю вы создали список {list_name}"


class Keyboards:
    @classmethod
    def get_list(cls, cur_user: User) -> t.types.InlineKeyboardMarkup:
        keyboard = t.types.InlineKeyboardMarkup()
        a = cur_user.lists
        for l_text, l_callback in cur_user.lists:
            callback_button = t.types.InlineKeyboardButton(text=l_text, callback_data=l_callback)
            keyboard.add(callback_button)
        return keyboard

    @classmethod
    def get_inline_keyboard(cls, user_id):
        keyboard = t.types.InlineKeyboardMarkup()
        for t_text, t_callback in User.get_all_tasks(tg_id=user_id):
            callback_button = t.types.InlineKeyboardButton(text=t_text, callback_data=t_callback)
            keyboard.add(callback_button)
        return keyboard

    @classmethod
    def get_main_menu(cls):
        return "Выберете команду на клавиатуре"
