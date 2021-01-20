from contextlib import contextmanager
import typing
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, MetaData

from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False)
Session = sessionmaker(bind=engine)
current_session = scoped_session(Session)

Base = declarative_base()


@contextmanager
def session(**kwargs) -> typing.ContextManager[Session]:
    """Provide a transactional scope around a series of operations."""
    new_session = Session(**kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


from threading import local


class SessionRegistry(local):
    session = None


registry = SessionRegistry()

class Middleware:

    @staticmethod
    def on_request_start(request=''):
        registry.session = Session()
        # registry.session = current_session()

    @staticmethod
    def on_request_error( error=''):
        registry.session.rollback()
        registry.session.close()
        registry.session = None

    @staticmethod
    def on_response(response=''):
        registry.session.commit()
        registry.session.close()
        registry.session = None


@contextmanager
def session_thread(**kwargs):
    """Provide a transactional scope around a series of operations."""
    mw = Middleware()
    try:
        mw.on_request_start()
    except Exception:
        mw.on_request_error('')
    finally:
        mw.on_response()
