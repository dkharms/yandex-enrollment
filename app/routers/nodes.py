import typing as t

from uuid import UUID
from logging import Logger
from datetime import datetime

from fastapi import APIRouter, Depends, status, Response
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND

import app.schemas as s
import app.models as m

from app.utils import LoggerProxy, DatabaseProxy, ConfigProxy

nodes_router = APIRouter(tags=["Must Have Endpoints"])


def get_category_entities(current_entity: m.ShopUnit, db: Session, log: Logger):
    log.info(f"getting node data for {current_entity.id}")
    current_model = s.ShopUnit.from_orm(current_entity)

    if current_entity.parent is not None:
        current_model.parent_id = current_entity.parent.id
    current_amount, current_sum = 0, 0

    if current_model.type == s.ShopUnitType.category:
        current_model.children = []
    else:
        current_model.children = None
        current_amount, current_sum = 1, current_model.price

    for child_entity in current_entity.children:
        child_model, child_amount, child_sum = get_category_entities(
            child_entity, db, log,
        )
        current_amount += child_amount
        current_sum += child_sum

        current_model.children.append(child_model)

    if current_model.type == s.ShopUnitType.category and current_amount == 0:
        current_model.price = None
    elif current_model.type == s.ShopUnitType.category:
        current_model.price = int(current_sum / current_amount)

    return current_model, current_amount, current_sum


@nodes_router.get("/nodes/{id}", response_model=s.ShopUnit)
def nodes_info(id: UUID, db: Session = Depends(DatabaseProxy), log: Logger = Depends(LoggerProxy)):
    log.info(f"got nodes request for {id}")

    item_model = db.query(m.ShopUnit).get(str(id))
    if item_model is None:
        error = s.Error(code=404, message="Item not found")
        return Response(content=error.json(), status_code=404)

    current_model, _, _ = get_category_entities(item_model, db, log)

    return current_model
