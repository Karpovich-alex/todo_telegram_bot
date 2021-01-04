from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Boolean, exc, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import Config

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(128))
    tg_id = Column(Integer, unique=True)

    def __repr__(self):
        return "<User id: {id} username: {username}>".format(id=self.id, username=self.username)


class Task(Base):
    __tablename__='tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User, backref=backref('tasks'))
    text = Column(String(128))
    is_completed = Column(Boolean, default=False)
    created_time = Column(DateTime, default=func.now())

    def __repr__(self):
        return "Task id: {id} created by user id: {user_id}".format(id=self.id, user_id=self.user_id)



# u1 = User(username='Egor')
# s.add(u1)
# s.commit()
#
# print(s.query(User).all())
