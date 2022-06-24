import os
import loguru

from loguru import logger

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base


class Config(object):
    def __init__(self, ip, port) -> None:
        self.ip = ip
        self.port = port

    @classmethod
    def restore_from_env(cls):
        ip = os.getenv("IP", "0.0.0.0")
        port = os.getenv("PORT", "80")

        os.makedirs("instances", exist_ok=True)
        os.makedirs("logs", exist_ok=True)

        return cls(ip=ip, port=port)

    def __call__(self) -> "Config":
        return self


class Logger(object):
    def __init__(self, name, filename) -> None:
        logger.remove()
        logger.add(
            filename, format="[{level}] ({time}) <{function}>: {message}", colorize=True
        )

    @classmethod
    def restore_from_env(cls):
        name = os.getenv("APP_NAME", "app")
        filename = os.getenv("FILENAME", "logs/dev.log")

        return Logger(name=name, filename=filename)

    def __call__(self) -> "loguru.Logger":
        return logger


class Database(object):
    def __init__(self, database_url) -> None:
        self.SQLALCHEMY_DATABASE_URL = database_url
        self.__engine = create_engine(
            self.SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
        self.__SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.__engine
        )

    @classmethod
    def restore_from_env(cls):
        database_url = os.getenv(
            "DATABASE_URL", "sqlite:///instances/dev-sql.db"
        )

        return Database(database_url=database_url)

    def init(self):
        Base.metadata.create_all(bind=self.__engine)

    @property
    def engine(self):
        return self.__engine

    def __call__(self):
        session = self.__SessionLocal()
        try:
            yield session
        finally:
            session.close()


ConfigProxy = Config.restore_from_env()
LoggerProxy = Logger.restore_from_env()
DatabaseProxy = Database.restore_from_env()
