from models import User, Task, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, exc
from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False)
session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
s = session()


class UserDb:

    @classmethod
    def get_user(cls, user=None, **filter_args):
        if user:
            filter_args = {'tg_id': user.id}  # for user from tg
        if not filter_args:
            raise Exception
        if cls.check_user(**filter_args):
            u = s.query(User).filter_by(**filter_args).first()
            return u
        else:
            if user:
                return cls.create_user(user)
            else:
                raise Exception

    @classmethod
    def create_user(cls, user):
        u = User(username=user.username, tg_id=user.id)
        s.add(u)
        s.commit()
        print(f"ADD USER {user.id} name: {user.username}")
        return u

    @classmethod
    def check_user(cls, user=None, **filter_args):
        if user:
            filter_args = {'tg_id': user.id}  # for user from tg
        u = s.query(User).filter_by(**filter_args).first()
        if u:
            return True
        else:
            return False

    @classmethod
    def add_task(cls, text, tg_id):
        t = Task(text=text, user_id=cls.get_user(tg_id=tg_id).id)
        s.add(t)
        s.commit()

    @classmethod
    def edit_task(cls, t_id=0, t_text=None, t_status=None, callback_data=None):
        if callback_data:
            callback_data = TaskDb.parse_callback_data(callback_data)
            t_id = callback_data['id']
            t_status = bool(callback_data['is_completed'])
        t: Task = cls.get_task(t_id)
        if t_text:
            t.text = t_text
        if t_status != None:
            t.is_completed = t_status
        s.add(t)
        s.commit()

    @classmethod
    def get_task(cls, t_id):
        t = s.query(Task).filter_by(id=t_id).first()
        if t:
            return t
        else:
            return None

    @classmethod
    def get_all_tasks(cls, tg_id=0):
        """
        Returm list with task text and task data callback [[task_1.text, task_1.callback],...]
        :param tg_id:
        :return:
        """
        if not tg_id:
            return ''
        u = cls.get_user(tg_id=tg_id)
        t_mas = []
        for t in sorted(u.tasks, key=lambda t: t.id):
            t_mas.append(TaskDb.prepare_task_info(t))
        return t_mas
        # return '\n'.join(map(lambda x: str(x[0]) + ' ' + str(x[1].text), enumerate(u.tasks)))


class TaskDb:

    @classmethod
    def prepare_task_info(cls, t: Task):
        return [cls.get_task_text(t), cls.get_task_callback_data(t)]

    @classmethod
    def get_task_text(cls, t: Task):
        return f"{'✅' if t.is_completed else '❌'} {t.text}"

    @classmethod
    def get_task_callback_data(cls, t: Task):
        is_completed = 0 if t.is_completed else 1
        return "t {id}, {user_id}, {is_completed}".format(id=t.id, user_id=t.user_id,
                                                          is_completed=is_completed)

    @classmethod
    def parse_callback_data(cls, callback_data: str):
        callback_data = callback_data[1:].split(',')
        return {'id': int(callback_data[0]), 'user_id': int(callback_data[1]), 'is_completed': int(callback_data[2])}
