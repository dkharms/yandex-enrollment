import json
import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.schemas as s
import app.models as m

from app import app
from app.test.fixtures import db

client = TestClient(app)


@pytest.mark.order(6)
def test_delete_node(db: Session):
    with open("app/test/imports.json", "r") as file:
        data = json.loads(file.read())

    id = data["items"][-1]["id"]

    response = client.delete(
        f"/delete/{id}",
    )

    assert response.status_code == 200

    unit_model = db.query(m.ShopUnit).get(id)
    assert unit_model is None

    response = client.delete(
        f"/delete/{id}",
    )

    assert response.status_code == 404
