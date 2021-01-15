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
    from database.base import Middleware

    mw = Middleware()


class UserCase(unittest.TestCase):
    def setUp(self):
        mw.on_request_start('')
        Base.metadata.create_all(engine)
        self.s = current_session()
        self.u1 = User(username='first', tg_id=1111)
        self.u2 = User(username='second', tg_id=2222)
        self.s.add(self.u1)
        self.s.add(self.u2)
        self.s.commit()

    def tearDown(self):
        mw.on_response('')
        # self.s.remove()
        Base.metadata.drop_all(engine)

    def test_create_user(self):
        # u = User.create_user(username='user', tg_id=1)
        # s=c.session()
        # def find_user(tg_id):
        #     return s.query(UserDb).filter_by(tg_id=tg_id).first
        # self.assertEqual(u, self.s.query(UserDb).filter_by(tg_id=1).first)
        with self.assertRaises(AttributeError):
            User.create_user(username='user', tg_id=1)
        with self.assertRaises(AttributeError):
            User.create_user(tg_id=1)
        with self.assertRaises(AttributeError):
            User.create_user(username='user')

    def test_get_user(self):
        m1 = SimpleClass(from_user=SimpleClass(username='first', id=1111))
        u1 = User.get_user(message=m1)
        self.assertEqual(self.u1, u1)
        m2 = SimpleClass(from_user=SimpleClass(username='second', id=2222))
        u2 = User.get_user(message=m2)
        self.assertNotEqual(self.u1, u2)

    def test_check_user(self):
        f_user = SimpleClass(username='first', id=10)
        self.assertFalse(User.check_user(tg_user=f_user))
        self.assertTrue(User.check_user(db_user=self.u1))


class ListCase(unittest.TestCase):
    def setUp(self):
        mw.on_request_start('')
        Base.metadata.create_all(engine)
        self.s: session = current_session()
        self.u1 = User(username='first', tg_id=1111)
        self.list1 = List(name='first list', users=self.u1)
        self.s.add(self.u1)
        self.s.add(self.list1)
        self.s.commit()

    def tearDown(self):
        mw.on_response('')
        Base.metadata.drop_all(engine)

    def test_check_list(self):
        self.assertTrue(List.list_exist(name='first list', user=self.u1))
        self.assertFalse(List.list_exist(name='fake list', user=self.u1))

    def test_create_list(self):
        # new_list=List(name='new list', users=self.u1)
        self.assertTrue(List.create_list(name='new list', user=self.u1))
        self.assertFalse(List.create_list(name='new list', user=self.u1))
        new_list = self.s.query(User).join(List).filter_by(name='new list').first()
        self.assertIsNotNone(new_list)


if __name__ == '__main__':
    unittest.main(verbosity=2)
