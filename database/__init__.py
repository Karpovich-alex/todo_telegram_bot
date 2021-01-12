from database.models import User, Task, List
from database.base import Base, current_session, engine


def create():
    Base.metadata.create_all(engine)
