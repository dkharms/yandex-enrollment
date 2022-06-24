import typing as t

from logging import Logger
from datetime import datetime

from fastapi import APIRouter, Depends, status, Response
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

import app.schemas as s
import app.models as m

from app.utils import LoggerProxy, DatabaseProxy

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
            raise RequestValidationError(errors=["Validation Failed"])
        seen_ids.add(item.id)

    return seen_ids


def validate_parent_entity(
        items: t.List[s.ShopUnitImport], shop_unit_graph: ShopUnitGraph,
        db: Session, log: Logger
):
    for item in items:
        log.info(
            f"validating parent entity: id={item.id} parent_id={item.parent_id}"
        )

        if item.parent_id is None:
            continue

        if item.parent_id in shop_unit_graph:
            parent_item = shop_unit_graph[item.parent_id]
            if parent_item.type == s.ShopUnitType.offer:
                raise RequestValidationError(errors=["Validation Failed"])
            continue

        item_model = db.get(m.ShopUnit, str(item.parent_id))
        if item_model is None:
            raise RequestValidationError(errors=["Validation Failed"])

        if item_model.type == s.ShopUnitType.offer:
            raise RequestValidationError(errors=["Validation Failed"])


def validate_type_consistency(items: t.List[s.ShopUnitImport], db: Session, log: Logger):
    for item in items:
        log.info(f"validating type consistency: id={item.id}")

        item_model = db.get(m.ShopUnit, str(item.id))
        if item_model is not None and item_model.type != item.type:
            raise RequestValidationError(errors=["Validation Failed"])


def update_parent_date(item: m.ShopUnit, update_date: datetime, db: Session, log: Logger):
    log.info(f"updating item: id={item.id} update_date={update_date}")

    item.date = update_date  # pyright: ignore
    db.commit()

    log.info(f"updated item: id={item.id} update_date={update_date}")
    if item.parent is not None:
        update_parent_date(item.parent, update_date, db, log)


def create_or_update(item: s.ShopUnitImport, update_date: datetime, db: Session, log: Logger):
    item_model = db.get(m.ShopUnit, str(item.id))

    if item_model is not None:
        item_model.name = item.name
        item_model.date = update_date
        item_model.parent_id = str(item.parent_id)
        item_model.price = item.price
    else:
        item_model = m.ShopUnit(
            id=str(item.id), name=item.name,
            date=update_date, parent_id=str(item.parent_id),
            type=item.type, price=item.price,
        )
        db.add(item_model)
    db.commit()


@imports_router.post("/imports")
async def import_entities(
        import_request: s.ShopUnitImportRequest,
        db: Session = Depends(DatabaseProxy), log: Logger = Depends(LoggerProxy)
):
    log.info(f"got request for import: amount={len(import_request.items)}")

    shop_unit_graph = ShopUnitGraph(import_request.items)
    shop_unit_graph.sort()

    validate_unique_ids(import_request.items)
    validate_type_consistency(import_request.items, db, log)
    validate_parent_entity(import_request.items, shop_unit_graph, db, log)

    for item in shop_unit_graph:
        create_or_update(item, import_request.update_date, db, log)
        if item.parent_id is not None and item.parent_id not in shop_unit_graph:
            item_model = db.query(m.ShopUnit).get(str(item.id))
            update_parent_date(item_model, import_request.update_date, db, log)

    return Response(status_code=status.HTTP_200_OK)
