import logging
import typing as t

from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, status, Response
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

import app.schemas as s
import app.models as m

from app.utils import LoggerProxy, DatabaseProxy

imports_router = APIRouter(tags=["Required Endpoints"])


def validate_unique_ids(items: t.List[s.ShopUnitImport]):
    seen_ids = {}

    for item in items:
        if item.id in seen_ids:
            raise RequestValidationError(errors=["Validation Failed"])
        seen_ids[item.id] = item

    return seen_ids


def validate_parent_entity(
        items: t.List[s.ShopUnitImport], items_dict: t.Dict[UUID, s.ShopUnitImport],
        db: Session, log: logging.Logger
):
    for item in items:
        log.debug(
            f"validating parent entity: id={item.id} parent_id={item.parent_id}"
        )

        # If entity has no parent, then we skip it.
        if item.parent_id is None:
            continue

        # If entity has parent in POST body items, then we should check
        # if parent has type of CATEGORY.
        if item.parent_id in items_dict:
            parent_item = items_dict[item.parent_id]
            if parent_item.type == s.ShopUnitType.offer:
                raise RequestValidationError(errors=["Validation Failed"])
            continue

        # If entity's field parent_id is set, but parent doesn't contain in
        # POST body items or in database, then we should fail.
        item_model = db.get(m.ShopUnit, str(item.parent_id))
        if item_model is None:
            raise RequestValidationError(errors=["Validation Failed"])

        if item_model.type == s.ShopUnitType.offer:
            raise RequestValidationError(errors=["Validation Failed"])


def validate_type_consistency(items: t.List[s.ShopUnitImport], db: Session, log: logging.Logger):
    for item in items:
        log.debug(f"validating type consistency: id={item.id}")

        item_model = db.get(m.ShopUnit, str(item.id))
        if item_model is not None and item_model.type != item.type:
            raise RequestValidationError(errors=["Validation Failed"])


def update_parent_date(item: m.ShopUnit, update_date: datetime, db: Session, log: logging.Logger):
    log.debug(f"updating item: id={item.id} update_date={update_date}")

    item.date = update_date  # pyright: ignore

    log.info(f"updated item: id={item.id} update_date={update_date}")
    if item.parent is not None:
        update_parent_date(item.parent, update_date, db, log)


def create_or_update_unit(unit_schema: s.ShopUnitImport, update_date: datetime, db: Session, log: logging.Logger):
    log.debug(f"creating or updating: {unit_schema.id=} {unit_schema.type=}")
    unit_model = db.get(m.ShopUnit, str(unit_schema.id))

    if unit_model is not None:
        unit_model.name, unit_model.date = unit_schema.name, update_date
        unit_model.parent_id = str(unit_schema.parent_id)
        unit_model.price = unit_schema.price
    else:
        unit_model = m.ShopUnit(
            id=str(unit_schema.id), name=unit_schema.name,
            date=update_date, parent_id=str(unit_schema.parent_id),
            type=unit_schema.type, price=unit_schema.price,
        )
        db.add(unit_model)

    db.flush()


@imports_router.post("/imports")
async def import_units(
        import_request: s.ShopUnitImportRequest,
        db: Session = Depends(DatabaseProxy), log=Depends(LoggerProxy)
):
    log.info(f"got imports request: {len(import_request.items)}")

    unit_schemas_dict = validate_unique_ids(import_request.items)
    validate_type_consistency(import_request.items, db, log)
    validate_parent_entity(import_request.items, unit_schemas_dict, db, log)

    for unit_schema in unit_schemas_dict.values():
        create_or_update_unit(unit_schema, import_request.update_date, db, log)

        # If entity has parent and its parent not in POST body, then we should
        # update parent date in database.
        if unit_schema.parent_id is not None and unit_schema.parent_id not in unit_schemas_dict:
            unit_model = db.query(m.ShopUnit).get(str(unit_schema.id))
            update_parent_date(unit_model, import_request.update_date, db, log)

    db.commit()

    return Response(status_code=status.HTTP_200_OK)
