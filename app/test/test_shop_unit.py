import uuid as u

from datetime import datetime

from fastapi.testclient import TestClient

import app.schemas as s
import app.models as m

from app import app
from app.utils import DatabaseProxy
from app.test.fixtures import db


data = {
    "items": [
        {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "string",
            "parentId": None,
            "type": "CATEGORY",
            "price": None
        },
        {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa5",
            "name": "string",
            "parentId": "3fa85f64-5717-4562-b3fc-2c963f66afa4",
            "type": "CATEGORY",
            "price": None
        },
        {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
            "name": "string",
            "parentId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "type": "CATEGORY",
            "price": None
        },
        {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
            "name": "string",
            "parentId": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
            "type": "CATEGORY",
            "price": None
        },
        {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa9",
            "name": "string",
            "parentId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "type": "OFFER",
            "price": 0
        },
    ],
    "updateDate": "2022-06-22T10:38:57.760Z"
}

client = TestClient(app)
DatabaseProxy.init()


def test_graph_dependecies_handling():
    from app.routers.imports import ShopUnitGraph

    expected = [
        u.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa5"),
        u.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
        u.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa9"),
        u.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa7"),
        u.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa8"),
    ]

    import_request = s.ShopUnitImportRequest.parse_obj(data)

    shop_unit_graph = ShopUnitGraph(import_request.items)
    shop_unit_graph.sort()

    sorted_units = list(map(lambda x: x.id, shop_unit_graph))
    assert expected == sorted_units


def test_create_category(db):
    unit = s.ShopUnitImport(
        id=u.uuid4(), name="Some Name",
        parentId=None, type=s.ShopUnitType.category, price=None,
    )

    request = s.ShopUnitImportRequest(
        items=[unit],
        updateDate=datetime.now(),
    )
    response = client.post(
        "/imports", data=request.json(by_alias=True),
        headers={
            "Content-Type": "application/json; charset=utf-8"
        }
    )
    assert response.status_code == 200

    model = db.query(m.ShopUnit).get(str(unit.id))
    assert model is not None
    assert model.name == unit.name


def test_create_offer(db):
    unit = s.ShopUnitImport(
        id=u.uuid4(), name="Some Name",
        parentId=None, type=s.ShopUnitType.offer, price=200,
    )

    request = s.ShopUnitImportRequest(
        items=[unit],
        updateDate=datetime.now(),
    )
    response = client.post(
        "/imports", data=request.json(by_alias=True),
        headers={
            "Content-Type": "application/json; charset=utf-8"
        }
    )
    assert response.status_code == 200

    model = db.query(m.ShopUnit).get(str(unit.id))
    assert model is not None
    assert model.name == unit.name
