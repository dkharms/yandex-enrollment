import pytest

from app.utils import DatabaseProxy


@pytest.fixture(scope="session")
def db():
    yield from DatabaseProxy()
    DatabaseProxy.destroy()
