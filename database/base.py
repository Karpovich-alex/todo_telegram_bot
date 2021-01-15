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
    def on_request_start(self, request=''):
        registry.session = Session()

    def on_request_error(self, error):
        registry.session.close()
        registry.session = None

    def on_response(self, response=''):
        registry.session.commit()
        registry.session.close()
        registry.session = None

@contextmanager
def session_thread(**kwargs):
    """Provide a transactional scope around a series of operations."""
    mw=Middleware()
    try:
        mw.on_request_start()
    except Exception:
        mw.on_request_error('')
    finally:
        mw.on_response()