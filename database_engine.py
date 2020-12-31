from sqlalchemy import create_engine
from models import Base, User, Task

engine = create_engine('sqlite:///:memory:')
from sqlalchemy.orm import sessionmaker, scoped_session

session = scoped_session(sessionmaker(bind=engine))

Base.metadata.create_all(engine)

s = session()


class UserDb(User):
    def get_by_tg_id(self, tg_id: int):
        return s.query(User).filter_by(tg_id=tg_id).first()


u1 = User(nickname='Egor')
s.add(u1)
t1 = Task(user_id=1, text='First task')
t2 = Task(user_id=1, text='Second task')
s.add(t1)
s.add(t2)
# s.commit()
