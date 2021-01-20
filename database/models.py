from typing import Optional
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Boolean, JSON
from sqlalchemy.orm import relationship, backref, session

import json

from database.base import Base
from database.base import current_session as s

s: session


class ParsertoJson:

    def get_json(self, **kwargs) -> str:
        '''
        Create json str
        :param kwargs: if value == None then update it with value from class, else dont change value.
        :return:
        '''
        for k in kwargs.keys():
            if k in self.__dict__ and not kwargs[k]:
                kwargs[k] = getattr(self, k)
        output_json = json.dumps(kwargs)
        return output_json


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(128))
    tg_id = Column(Integer, unique=True)
    register_time = Column(DateTime, default=func.now())

    _step_id = Column(Integer, ForeignKey('user_step.id'), default=1)
    _step = relationship('UserStep', back_populates='user')

    list_id = Column(Integer, ForeignKey('lists.id'))
    lists = relationship('List')

    def __repr__(self):
        return "<User id: {id} username: {username}>".format(id=self.id, username=self.username)

    @classmethod
    def check_user(cls, tg_user=None, db_user=None, **filter_args):
        if tg_user:
            filter_args = {'tg_id': tg_user.id, 'username': tg_user.username}  # for user from tg
        if db_user:
            filter_args = {'tg_id': db_user.tg_id, 'username': db_user.username}  # for user from DataBase
        u = s.query(User).filter_by(**filter_args).first()
        if u:
            return True
        else:
            return False

    @classmethod
    def create_user(cls, **kwargs) -> 'User':
        if cls.check_user(**kwargs):
            raise AttributeError('This user has already exist')
        else:
            if kwargs.get('username', False) and kwargs.get('tg_id', False):
                u = User(username=kwargs['username'], tg_id=kwargs['tg_id'])
                s.add(u)
                s.commit()
                return u
            else:
                raise AttributeError('Cant find username or tg_id')

    @classmethod
    def get_user(cls, message=None, **filter_args) -> 'User':
        if message:
            filter_args = {'tg_id': message.from_user.id, 'username': message.from_user.username}
        if not filter_args:
            raise AttributeError('Cant find attributes')
        if cls.check_user(**filter_args):
            return s.query(User).filter_by(**filter_args).first()
        else:
            return cls.create_user(**filter_args)

    def create_list(self, _list: 'List'):
        self.lists.append(_list)
        s.add(self)
        s.commit()

    @property
    def step(self):
        return self._step.step

    @step.setter
    def step(self, v):
        self._step_id = v
        s.add(self)
        s.commit()

    @step.getter
    def step(self):
        return self._step.step

    @property
    def step_info(self):
        return self._step.info

    @step_info.setter
    def step_info(self, v):
        self._step.info = v
        s.add(self)
        s.commit()

    @step_info.getter
    def step_info(self):
        return self._step.info


class List(Base, ParsertoJson):
    __tablename__ = 'lists'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    created_time = Column(DateTime, default=func.now())

    # users = relationship(User, backref=backref('lists'))
    users = relationship(User)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    tasks = relationship('Task', backref=backref('list'))

    # enable_typechecks=False
    # __mapper_args__ = {'enable_typechecks':False}

    def __repr__(self):
        return f"<List id: {self.id} name: {self.name}>"

    @classmethod
    def create_list(cls, name: str, user: User) -> bool:
        if not cls.list_exist(name, user):
            _list = List(name=name, users=user)
            s.add(_list)
            s.commit()
            return True
        else:
            return False

    @classmethod
    def list_exist(cls, name: str, user) -> bool:
        '''
        :return: True is list exist
        '''
        return bool(s.query(List).filter_by(user_id=user.id, name=name).first())

    @property
    def get_json(self, **kwargs) -> str:
        return super().get_json(type='List', id=None)

    def add_task(self, task: 'Task'):
        self.tasks.append(task)
        s.add(self)
        s.commit()

    @classmethod
    def get_list(cls, list_id):
        if not list_id:
            raise AttributeError('id is required')
        _list = s.query(cls).filter_by(id=list_id).first()
        if _list:
            return None
        else:
            return _list


class Task(Base, ParsertoJson):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    text = Column(String(128))
    is_completed = Column(Boolean, default=False)
    created_time = Column(DateTime, default=func.now())

    def __repr__(self):
        return "<Task id: {id}>".format(id=self.id)

    @property
    def get_json(self, **kwargs) -> str:
        return super(Task, self).get_json(type='Task', id=None, list_id=None, is_completed=None)

    @property
    def inline_text(self):
        return f"{'✅' if self.is_completed else '❌'} {self.text}"

    @classmethod
    def get_task(cls, task_id) -> Optional['Task']:
        task = s.query(cls).filter_by(id=task_id).first()
        if task:
            return task
        else:
            return None

    def change_status(self):
        self.is_completed = not self.is_completed
        s.add(self)
        s.commit()


class UserStep(Base):
    """
    Содержит номер шага на котором сейчас находится пользователь
    0-Главное меню
    1-Cоздание списка
    2-Список со списками задач
    3-Выбран список
    """
    __tablename__ = 'user_step'
    id = Column(Integer, primary_key=True)
    # user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates='_step')
    step = Column(Integer)
    info = Column(JSON)

    def __repr__(self):
        return f"<Step id: {self.id}"
