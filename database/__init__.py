from database.models import User, Task, List, UserStep
from database.base import Base, current_session, engine, Middleware


def init_db():
    Base.metadata.create_all(engine)
    u1 = UserStep(step=1)
    u2 = UserStep(step=2)
    # u3=UserStep(step=3)
    current_session.add_all([u1,u2])
    try:
        current_session.commit()
    except BaseException:
        current_session.rollback()
