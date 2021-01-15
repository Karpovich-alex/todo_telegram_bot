import unittest
from unittest.mock import patch
from sqlalchemy.orm import session

from tests.TestConfig import TestConfig


class SimpleClass:
    def __init__(self, **kw):
        for k, v in kw.items():
            self.__setattr__(k, v)


with patch('config.Config', new=TestConfig()) as mock:
    # mock=TestConfig()
    from database import User, List, current_session, Base, engine
    from database.base import Middleware, session_thread
    # from messages import Keyboards
    mw = Middleware()


class KeyboardsCase(unittest.TestCase):
    def setUp(self):
        mw.on_request_start('')
        Base.metadata.create_all(engine)
        self.s = current_session()
        self.u1 = User(username='first', tg_id=1111)
        self.list1 = List(name='first list', users=self.u1)
        self.s.add(self.u1)
        # self.s.commit()
        self.s.add(self.list1)
        self.s.commit()

    def tearDown(self):
        mw.on_response('')
        Base.metadata.drop_all(engine)

    def test_get_list_1(self):
        return_value = Keyboards.get_list(self.u1)

    def test_get_list(self):
        @session_thread()
        def a():
            return Keyboards.get_list(self.u1)

        res = a()
