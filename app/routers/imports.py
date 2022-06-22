import logging
import typing as t

from datetime import datetime

from fastapi import APIRouter, Depends, status, Response
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

import app.schemas as s
import app.models as m

from app.utils import LoggerProxy, DatabaseProxy, ConfigProxy

imports_router = APIRouter(tags=["Must Have Endpoints"])


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


def validate_unique_ids(items: t.List[s.ShopUnitImport]):
    seen_ids = set()

    for item in items:
        if item.id in seen_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Ids must be unique!")
        seen_ids.add(item.id)

    return seen_ids


def validate_parent_entity(items: t.List[s.ShopUnitImport], shop_unit_graph: ShopUnitGraph, db: Session):
    for item in items:
        if item.parent_id is None:
            continue

        if item.parent_id in shop_unit_graph:
            parent_item = shop_unit_graph[item.parent_id]
            if parent_item.type == s.ShopUnitType.offer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Parent entity must category!")
            continue

        item_model = db.get(m.ShopUnit, str(item.parent_id))
        if item_model is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Parent entity must exist!")

        if item_model.type == s.ShopUnitType.offer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Parent entity must be category!")


def validate_type_consistency(items: t.List[s.ShopUnitImport], db: Session):
    for item in items:
        item_model = db.get(m.ShopUnit, str(item.id))
        if item_model is not None and item_model.type != item.type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Entity type must be consistent!")


def create_or_update(item: s.ShopUnitImport, update_date: datetime, db: Session, log: logging.Logger):
    log.info(f"updating or creating {item.id=} {item.name=} {item.type=}")

    item_model = db.get(m.ShopUnit, str(item.id))
    if item_model is not None:
        item_model.name = item.name
        item_model.date = update_date
        item_model.parent_id = str(item.parent_id)
        item_model.price = item.price
    else:
        item_model = m.ShopUnit(
            id=str(item.id),
            name=item.name,
            date=update_date,
            parent_id=str(item.parent_id),
            type=item.type,
            price=item.price,
        )

    db.add(item_model)
    db.commit()

    log.info(f"finished updating or creating {item.id=}")


@imports_router.post("/imports")
async def import_entities(
        import_request: s.ShopUnitImportRequest,
        db: Session = Depends(DatabaseProxy), log=Depends(LoggerProxy)
):
    shop_unit_graph = ShopUnitGraph(import_request.items)
    shop_unit_graph.sort()

    validate_unique_ids(import_request.items)
    validate_type_consistency(import_request.items, db)
    validate_parent_entity(import_request.items, shop_unit_graph, db)

    log.info(f"updating or creating {len(import_request.items)} items")
    for item in shop_unit_graph:
        create_or_update(item, import_request.update_date, db, log)

    return Response(status_code=status.HTTP_200_OK)
