import typing as t

from pprint import pprint
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

import app.schemas as s
import app.models as m

from app.dependencies import get_db
from app.schemas import shop_unit


imports_router = APIRouter()


class ShopUnitGraph(object):
    def __init__(self, items: t.List[s.ShopUnitImport]) -> None:
        self.__mark = {item.id: False for item in items}
        self.__graph = {item.id: [] for item in items}
        self.__has_parent = {item.id: False for item in items}
        self.__items = items
        self.__order = []

        self.__build_graph()

    def __build_graph(self) -> None:
        for item in self.__items:
            if item.parent_id is None or item.parent_id not in self.__graph:
                continue
            self.__graph[item.parent_id].append(item.id)
            self.__has_parent[item.id] = True

    def is_valid(self) -> None:
        pass

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

    def __iter__(self):
        for id in self.__order:
            yield id


def validate_unique_ids(items: t.List[s.ShopUnitImport]):
    seen_ids = set()

    for item in items:
        if item.id in seen_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Ids must be unique!")
        seen_ids.add(item.id)

    return seen_ids


def validate_parent_category(item: s.ShopUnitImport):
    pass


@imports_router.post("/imports")
async def import_entities(import_request: s.ShopUnitImportRequest, db: Session = Depends(get_db)):
    validate_unique_ids(import_request.items)

    shop_unit_graph = ShopUnitGraph(import_request.items)
    shop_unit_graph.sort()

    return {"id": import_request.items[-1].id, "amount": len(import_request.items)}
