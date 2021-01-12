from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import relationship, backref, session

from database.base import Base
from database.base import current_session as s

s: session


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(128))
    tg_id = Column(Integer, unique=True)
    register_time = Column(DateTime, default=func.now())
    _step = relationship('UserStep', uselist=False, back_populates='user')

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


class List(Base):
    __tablename__ = 'lists'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    created_time = Column(DateTime, default=func.now())

    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(User, backref=backref('lists'))

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
        :param list_name:
        :param user:
        :return: True is list exist
        '''
        return bool(s.query(List).filter_by(user_id=user.id, name=name).first())


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    text = Column(String(128))
    is_completed = Column(Boolean, default=False)
    created_time = Column(DateTime, default=func.now())

    list_id = Column(Integer, ForeignKey('lists.id'))
    list = relationship(List, backref=backref('tasks'))

    def __repr__(self):
        return "<Task id: {id} in list id: {user_id}>".format(id=self.id, user_id=self.list_id)


class UserStep(Base):
    """
    Содержит номер шага на котором сейчас находится пользователь
    0-Главное меню
    1-создание списка
    2-Список со списками задач
    """
    __tablename__ = 'user_step'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates='_step')
    step = Column(Integer)

    def __repr__(self):
        return f"<User {self.user_id} on step {self.step}"
