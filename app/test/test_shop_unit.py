import pydantic
import pytest

from uuid import UUID

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


def test_graph_dependecies_handling():
    from app.routers.imports import ShopUnitGraph
    from app.schemas import ShopUnitImportRequest

    expected = [
        UUID("3fa85f64-5717-4562-b3fc-2c963f66afa5"),
        UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"), UUID("3fa85f64-5717-4562-b3fc-2c963f66afa9"),
        UUID("3fa85f64-5717-4562-b3fc-2c963f66afa7"), UUID("3fa85f64-5717-4562-b3fc-2c963f66afa8"),
    ]

    import_request = ShopUnitImportRequest.parse_obj(data)

    shop_unit_graph = ShopUnitGraph(import_request.items)
    shop_unit_graph.sort()

    sorted_units = list(shop_unit_graph)
    assert expected == sorted_units


def test_create_shop_units(db):
