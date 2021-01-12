from database import User, Task, List, Base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, exc
from config import Config
import typing
from database import current_session as s

# class Connector:
#
#     def __init__(self):
#         self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False)
#         self.session = sessionmaker(bind=self.engine)
#         self.Base = Base
#         self.create_all()
#
#     def create_all(self):
#         self.Base.metadata.create_all(self.engine)
#
#     def drop_all(self):
#         self.Base.metadata.drop_all(bind=self.engine)
#
#
# c = Connector()
#
# s = c.session()


class UserDb(User):
    def __eq__(self, other):
        if isinstance(other, User) or isinstance(other, UserDb):
            for k, v in other.__dict__.items():
                if not k.startswith('_'):
                    if self.__getattribute__(k) != other.__getattribute__(k):
                        return False
            return True
        else:
            return False

    @classmethod
    def get_user(cls, message=None, **filter_args) -> User:
        if message:
            filter_args = {'tg_id': message.from_user.id, 'username': message.from_user.username}
        if not filter_args:
            raise AttributeError('Cant find attributes')
        if cls.check_user(**filter_args):
            return s.query(User).filter_by(**filter_args).first()
        else:
            return cls.create_user(**filter_args)

    @classmethod
    def create_user(cls, **kwargs) -> User:
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
    def get_lists(cls) -> typing.List[typing.List[str]]:
        '''
        :return: Return list with task text and task data callback [[list_1.text, list_1.callback],...]
        '''
        s.query(User)
        return [['', '']]

    @property
    def step(self):
        return self._step

    @step.getter
    def step(self):
        return self._step.step

    @step.setter
    def step(self, step_num):
        self._step.step = step_num
        s.add(self)
        s.commit()

    # @classmethod
    # def add_task(cls, text, tg_id):
    #     t = Task(text=text, user_id=cls.get_user(tg_id=tg_id).id)
    #     s.add(t)
    #     s.commit()
    #
    # @classmethod
    # def edit_task(cls, t_id=0, t_text=None, t_status=None, callback_data=None):
    #     if callback_data:
    #         callback_data = TaskDb.parse_callback_data(callback_data)
    #         t_id = callback_data['id']
    #         t_status = bool(callback_data['is_completed'])
    #     t: Task = cls.get_task(t_id)
    #     if t_text:
    #         t.text = t_text
    #     if t_status != None:
    #         t.is_completed = t_status
    #     s.add(t)
    #     s.commit()
    #
    # @classmethod
    # def get_task(cls, t_id):
    #     t = s.query(Task).filter_by(id=t_id).first()
    #     if t:
    #         return t
    #     else:
    #         return None
    #
    # @classmethod
    # def get_all_tasks(cls, tg_id=0):
    #     """
    #     Return list with task text and task data callback [[task_1.text, task_1.callback],...]
    #     :param tg_id:
    #     :return:
    #     """
    #     if not tg_id:
    #         return ''
    #     u = cls.get_user(tg_id=tg_id)
    #     t_mas = []
    #     for t in sorted(u.tasks, key=lambda t: t.id):
    #         t_mas.append(TaskDb.prepare_task_info(t))
    #     return t_mas
    #     # return '\n'.join(map(lambda x: str(x[0]) + ' ' + str(x[1].text), enumerate(u.tasks)))


# class TaskDb:
#
#     @classmethod
#     def prepare_task_info(cls, t: Task):
#         return [cls.get_task_text(t), cls.get_task_callback_data(t)]
#
#     @classmethod
#     def get_task_text(cls, t: Task):
#         return f"{'✅' if t.is_completed else '❌'} {t.text}"
#
#     @classmethod
#     def get_task_callback_data(cls, t: Task):
#         is_completed = 0 if t.is_completed else 1
#         return "t {id}, {is_completed}".format(id=t.id, is_completed=is_completed)
#
#     @classmethod
#     def parse_callback_data(cls, callback_data: str):
#         callback_data = callback_data[1:].split(',')
#         return {'id': int(callback_data[0]), 'is_completed': int(callback_data[1])}


class ListDb(List):
    @classmethod
    def create_list(cls, list_name: str, user: User) -> bool:
        if cls.check_list(list_name, user):
            _list = List(name=list_name, users=user)
            s.add(_list)
            s.commit()
            return True
        else:
            return False

    @classmethod
    def check_list(cls, list_name: str, user) -> bool:
        return bool(s.query(List).filter_by(user_id=user.id, name=list_name).first())

# from alembic.config import Config
# from alembic import command
# alembic_cfg = Config("alembic.ini")
# command.stamp(alembic_cfg, "head")
