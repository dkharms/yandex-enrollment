import logging
import typing as t

from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

import app.schemas as s
import app.models as m

from app.utils import LoggerProxy, DatabaseProxy

nodes_router = APIRouter(tags=["Required Endpoints"])


def deep_get_unit_info(unit_model: m.ShopUnit, db: Session, log: logging.Logger) -> t.Tuple[s.ShopUnit, int, int]:
    log.debug(f"getting node data: {unit_model.id=} {unit_model.type=}")
    unit_schema = s.ShopUnit.from_orm(unit_model)

    if unit_model.parent is not None:
        unit_schema.parent_id = unit_model.parent.id
    current_amount, current_sum = 0, 0

    if unit_schema.type == s.ShopUnitType.category:
        unit_schema.children = []
    else:
        unit_schema.children = None
        current_amount, current_sum = 1, unit_schema.price

    for child_unit_model in unit_model.children:
        child_model, child_amount, child_sum = deep_get_unit_info(
            child_unit_model, db, log,
        )
        current_amount += child_amount
        current_sum += child_sum  # pyright: ignore

        unit_schema.children.append(child_model)  # pyright: ignore

    if unit_schema.type == s.ShopUnitType.category and current_amount == 0:
        unit_schema.price = None
    elif unit_schema.type == s.ShopUnitType.category:
        unit_schema.price = int(
            current_sum / current_amount  # pyright: ignore
        )

    return unit_schema, current_amount, current_sum  # pyright: ignore


@nodes_router.get("/nodes/{id}", response_model=s.ShopUnit)
def nodes_info(id: UUID, db: Session = Depends(DatabaseProxy), log: logging.Logger = Depends(LoggerProxy)):
    log.info(f"got nodes request: {id=}")

    unit_model = db.query(m.ShopUnit).get(str(id))
    if unit_model is None:
        error = s.Error(code=404, message="Item not found")
        return Response(content=error.json(), status_code=404, headers={
            "Content-Type": "application/json",
        })

    unit_schema, _, _ = deep_get_unit_info(unit_model, db, log)

    return unit_schema
