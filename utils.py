from typing import Callable, Tuple
import telebot

from database import User, Middleware


class Handler:

    @staticmethod
    def request_decorator(f) -> Callable:

        def dec(*params, **kw):
            Middleware.on_request_start()
            try:
                f(*params, **kw)
                Middleware.on_response()
            except Exception as e:
                Middleware.on_request_error(e)

        return dec

    @staticmethod
    def get_current_user(f) -> Callable:

        def dec(*params, **kw) -> Tuple[telebot.types.Message, User]:
            message: telebot.types.Message = f(*params, **kw)
            return message, Handler._get_current_user(message)

        return dec

    @staticmethod
    def _get_current_user(message: telebot.types.Message) -> User:
        return User.get_user(message=message)

    @staticmethod
    def get_user_step(message: telebot.types.Message) -> int:
        return Handler._get_current_user(message).step
