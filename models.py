from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    nickname = Column(String)
    tg_id = Column(Integer)

    def __repr__(self):
        print(f"<User id: {self.id} nickname: {self.nickname}")


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref=backref('tasks'))
    text = Column(String(128))
    is_completed = Column(Boolean, default=False)
    created_time = Column(DateTime, default=func.now())

    def __repr__(self):
        print(f"Task id: {self.id} created by user id: {self.user_id}")
