from models import User, Task, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, exc
from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)
session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
s = session()


class UserDb:

    @classmethod
    def get_user(cls, user=None, **filter_args):
        if user:
            filter_args = {'tg_id': user.id} # for user from tg
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
            filter_args = {'tg_id': user.id} # for user from tg
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
    def get_all_tasks(cls, tg_id=0):
        if not tg_id:
            return ''
        u = cls.get_user(tg_id=tg_id)
        return '\n'.join(map(lambda x: str(x[0]) + ' ' + str(x[1].text), enumerate(u.tasks)))
