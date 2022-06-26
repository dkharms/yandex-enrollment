import logging
import typing as t

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

import app.schemas as s
import app.models as m

from app.utils import LoggerProxy, DatabaseProxy

sales_router = APIRouter(tags=["Bonus Endpoints"])


def validate_date(date: str):
    try:
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    except Exception as e:
        raise RequestValidationError("Wrong update date format!")


@sales_router.get("/sales", response_model=s.ShopUnitSales)
async def sales(date: str, db: Session = Depends(DatabaseProxy), log: logging.Logger = Depends(LoggerProxy)):
    log.info(f"got sales request: {date=}")

    date_obj = validate_date(date)
    from_time = date_obj - timedelta(days=1)

    unit_models = db.query(m.ShopUnit).filter(
        (m.ShopUnit.type == s.ShopUnitType.offer) &
        (from_time <= m.ShopUnit.date) & (m.ShopUnit.date <= date_obj)
    ).all()

    response_schema = s.ShopUnitSales(items=[])
    for unit_model in unit_models:
        unit_schema = s.ShopUnit.from_orm(unit_model)

        if unit_model.parent_id is not None:
            unit_schema.parent_id = unit_model.parent_id

        unit_schema.children = None
        response_schema.items.append(unit_schema)

    return response_schema
