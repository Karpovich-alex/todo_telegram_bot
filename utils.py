from typing import Callable, Tuple, Optional
import json
import telebot

from database import User, Middleware


class Handler:

    def __init__(self, bot):
        self._bot = bot

    @staticmethod
    def request_decorator(f) -> Callable:

        def dec(*params, **kw):
            Middleware.on_request_start()
            try:
                res = f(*params, **kw)
                Middleware.on_response()
                return res
            except Exception as e:
                Middleware.on_request_error(e)

        return dec

    @staticmethod
    def get_current_user(f) -> Callable:

        def dec(message, *params, **kw) -> Tuple[telebot.types.Message, User]:
            current_user = Handler._get_current_user(message)
            return f(message, current_user, *params, **kw)

        return dec

    @staticmethod
    def get_current_user_callback(f) -> Callable:
        def dec(callback, *params, **kw):
            current_user = User.get_user(tg_id=callback.from_user.id)
            callback.info = json.loads(callback.data)
            return f(callback, current_user, *params, **kw)

        return dec

    def callback_query_handler(self, get_cur_user=True, *params, **kwargs):
        def dec(f):
            def dec_1(callback, *pars, **kw):
                if get_cur_user:
                    current_user = Handler._get_current_user(callback.message)
                else:
                    current_user = None
                callback.info = json.loads(callback.data)
                return f(callback, current_user, *pars, **kw)

            return dec_1

        self._bot.callback_query_handler(*params, **kwargs)
        return dec

    @staticmethod
    def _get_current_user(message: telebot.types.Message) -> User:
        return User.get_user(message=message)

    @staticmethod
    def get_user_step(message: telebot.types.Message) -> int:
        return Handler._get_current_user(message).step.step
