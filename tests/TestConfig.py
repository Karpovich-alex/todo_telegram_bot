from unittest.mock import MagicMock
class TestConfig(MagicMock):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    # :memory:?check_same_thread=False
    TESTING = True