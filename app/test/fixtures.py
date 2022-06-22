import pytest

from app.utils import DatabaseProxy


@pytest.fixture(scope="module")
def db():
    db = DatabaseProxy()
    yield from db
