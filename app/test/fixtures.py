import pytest

from app.utils import DatabaseProxy


@pytest.fixture(scope="session")
def db():
    DatabaseProxy.init()
    yield from DatabaseProxy()
