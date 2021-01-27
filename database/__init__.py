from database.models import User, Task, List, UserStep
from database.base import Base, current_session, engine, Middleware


def init_db():
    Base.metadata.create_all(engine)
