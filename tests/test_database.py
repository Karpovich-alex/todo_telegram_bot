import unittest
from unittest.mock import patch
from sqlalchemy.orm import session

from tests.TestConfig import TestConfig


class SimpleClass:
    def __init__(self, **kw):
        for k, v in kw.items():
            self.__setattr__(k, v)


with patch('config.Config', new=TestConfig()) as mock:
    from database import User, List, current_session, Base, engine, Task
    from database.models import UserStep
    from database.base import Middleware

    mw = Middleware()


class DBWorker:
    def setUp(self, *args, add_to_session=(), **kwargs):
        mw.on_request_start()
        Base.metadata.create_all(engine)
        self.s = current_session
        self.u1 = User(username='first', tg_id=1111)
        self.u2 = User(username='second', tg_id=2222)

        # self.s.commit()

        self.s.add(self.u1)
        self.s.add(self.u2)
        if add_to_session:
            self.s.add_all(add_to_session)
        self.s.commit()
        if self.u1.username != 'first':
            print('ERROR')

    def tearDown(self):
        mw.on_response('')
        Base.metadata.drop_all(engine)

    def create_new_session(self):
        mw.on_response('')
        mw.on_request_start('')
        self.s = current_session


class UserCase(DBWorker, unittest.TestCase):

    def setUp(self, *args, **kwargs):
        super(UserCase, self).setUp(add_to_session=(UserStep(step=1), UserStep(step=2)))

    def test_create_user(self):
        with self.assertRaises(AttributeError):
            User.create_user(tg_id=1111)
        with self.assertRaises(AttributeError):
            User.create_user(username='first')

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

    def test_step_getter(self):
        self.create_new_session()
        self.assertEqual(self.u1.step, 1)
        self.u1.step = 2
        self.assertEqual(self.u1.step, 2)


class ListCase(DBWorker, unittest.TestCase):

    def setUp(self, *args, **kwargs):
        super(ListCase, self).setUp(*args, **kwargs)
        self.list1 = List(name='first list', users=self.u1)
        self.s.add(self.list1)
        self.s.commit()

    def test_check_list(self):
        self.assertTrue(List.list_exist(name='first list', user=self.u1))
        self.assertFalse(List.list_exist(name='fake list', user=self.u1))

    def test_create_list(self):
        self.assertTrue(List.create_list(name='new list', user=self.u1))
        self.assertFalse(List.create_list(name='new list', user=self.u1))
        new_list = self.s.query(User).join(List).filter_by(name='new list').first()
        self.assertIsNotNone(new_list)

    def test_get_info_json(self):
        self.create_new_session()
        self.assertEqual(self.list1.get_json(), '{"type": "List", "id": 1}')


class MessageCase(DBWorker, unittest.TestCase):
    def setUp(self, *args, **kwargs):
        # super(MessageCase, self).setUp(*args, **kwargs)
        mw.on_request_start()
        Base.metadata.create_all(engine)
        self.s = current_session
        self.u1 = User(username='first', tg_id=1111)
        self.list1 = List(name='first list', users=self.u1)
        self.task1 = Task(text='first task', list=self.list1)
        self.s.add(self.u1)
        self.s.add(self.list1)
        self.s.add(self.task1)
        self.s.commit()
        if self.u1.username != 'first':
            print('ERROR')

    def test_get_task_json(self):
        str_json = '{"type": "Task", "id": 1, "list_id": 1}'
        # self.create_new_session()
        self.assertEqual(self.task1.get_json(), str_json)


if __name__ == '__main__':
    unittest.main(verbosity=2)
