import logging
import typing as t

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Logger(object):

    def __init__(self) -> None:
        formatter = logging.Formatter(
            '[%(levelname)s]:%(asctime)s:%(filename)s:%(funcName)s: %(message)s')

        self.log = logging.getLogger("app")
        self.log.setLevel(logging.DEBUG)

        ch = logging.FileHandler("info.log")
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)

        self.log.addHandler(ch)

    def __call__(self) -> t.Any:
        yield self.log


logger = Logger()
