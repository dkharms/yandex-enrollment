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


data = {
    "items": [
        {
            "id": "a1967a1b-e31a-423d-91f1-b68e31660c4d",
            "name": "a1967a1b-e31a-423d-91f1-b68e31660c4d",
            "parentId": None,
            "price": 56,
            "type": "OFFER"
        },
        {
            "id": "78fb7b2f-3bd1-4032-9266-3e2eebff93b0",
            "name": "78fb7b2f-3bd1-4032-9266-3e2eebff93b0",
            "parentId": None,
            "price": 62,
            "type": "OFFER"
        },
    ],
    "updateDate": "2022-06-25T22:36:06.339Z"
}


@pytest.mark.order(7)
def test_sales(db: Session):
    response = client.post(
        "/imports", data=json.dumps(data),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    assert response.status_code == 200
    response = client.get(
        f"/sales?date={data['updateDate']}",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
