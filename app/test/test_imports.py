import json
import uuid
import pytest

from datetime import date, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.schemas as s
import app.models as m

from app import app
from app.schemas.shop_unit import convert_datatime_to_valid_format
from app.test.fixtures import db

client = TestClient(app)


@pytest.mark.order(1)
def test_import_units(db: Session):
    with open("app/test/imports.json", "r") as file:
        data = json.loads(file.read())

    response = client.post(
        "/imports", data=json.dumps(data),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    assert response.status_code == 200
    assert db.query(m.ShopUnit).count() == len(data["items"])


@pytest.mark.order(2)
def test_import_dif_type_unit(db: Session):
    with open("app/test/imports.json", "r") as file:
        data = json.loads(file.read())

    types = ["OFFER", "CATEGORY"]
    unit_schema = data["items"][0]
    unit_schema["type"] = types[1 - types.index(unit_schema["type"])]

    response = client.post(
        "/imports", data=json.dumps(data),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    assert response.status_code == 400


@pytest.mark.order(3)
def test_import_wrong_parent_unit(db: Session):
    with open("app/test/imports.json", "r") as file:
        data = json.loads(file.read())

    data["items"][-1]["parentId"] = str(uuid.uuid4())

    response = client.post(
        "/imports", data=json.dumps(data),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    assert response.status_code == 400


@pytest.mark.order(4)
def test_import_parent_offer(db: Session):
    with open("app/test/imports.json", "r") as file:
        data = json.loads(file.read())

    data["items"][0]["parentId"] = data["items"][1]["id"]

    response = client.post(
        "/imports", data=json.dumps(data),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    assert response.status_code == 400

    data["items"][0]["parentId"] = data["items"][1]["id"]
    data["items"] = data["items"][0]

    response = client.post(
        "/imports", data=json.dumps(data),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    assert response.status_code == 400


@pytest.mark.order(4)
def test_import_unit_update(db: Session):
    with open("app/test/imports.json", "r") as file:
        data = json.loads(file.read())

    update_date = convert_datatime_to_valid_format(datetime.now())
    parent_id = data["items"][0]["parentId"]
    data["updateDate"] = update_date
    data["items"] = [data["items"][0]]

    response = client.post(
        "/imports", data=json.dumps(data),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    assert response.status_code == 200

    parent_unit_model = db.query(m.ShopUnit).get(parent_id)
    while parent_unit_model is not None:
        assert convert_datatime_to_valid_format(
            parent_unit_model.date) == update_date
        parent_unit_model = parent_unit_model.parent


@pytest.mark.order(5)
def test_import_same_ids(db: Session):
    with open("app/test/imports.json", "r") as file:
        data = json.loads(file.read())

    data["items"] = [data["items"][-1], data["items"][-1]]

    response = client.post(
        "/imports", data=json.dumps(data),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    assert response.status_code == 400
