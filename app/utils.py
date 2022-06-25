import os
import loguru
import typing as t

from loguru import logger

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.schemas as s

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
    def __init__(self, filename) -> None:
        logger.remove()
        logger.add(
            filename, format="[{level}] ({time}) <{function}>: {message}", colorize=True
        )

    @classmethod
    def restore_from_env(cls):
        filename = os.getenv("FILENAME", "logs/dev.log")

        return Logger(filename=filename)

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


class ShopUnitGraph(object):
    def __init__(self, items: t.List[s.ShopUnitImport]) -> None:
        self.__mark = {item.id: False for item in items}
        self.__graph = {item.id: [] for item in items}
        self.__has_parent = {item.id: False for item in items}
        self.__items = {item.id: item for item in items}
        self.__order = []

        self.__build_graph()

    def __build_graph(self) -> None:
        for item in self.__items.values():
            if item.parent_id is None or item.parent_id not in self.__graph:
                continue
            self.__graph[item.parent_id].append(item.id)
            self.__has_parent[item.id] = True

    def sort(self) -> None:
        for id in self.__graph:
            if not self.__has_parent[id]:
                self.__dfs(id)
        self.__order.reverse()

    def __dfs(self, current_id) -> None:
        self.__mark[current_id] = True
        for child_id in self.__graph[current_id]:
            if not self.__mark[child_id]:
                self.__dfs(child_id)
        self.__order.append(current_id)

    def __contains__(self, id) -> bool:
        return id in self.__items

    def __getitem__(self, id) -> s.ShopUnitImport:
        return self.__items[id]

    def __iter__(self):
        for id in self.__order:
            yield self.__items[id]


ConfigProxy = Config.restore_from_env()
LoggerProxy = Logger.restore_from_env()
DatabaseProxy = Database.restore_from_env()
