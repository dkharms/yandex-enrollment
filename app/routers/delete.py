import logging
import typing as t

from uuid import UUID

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

import app.schemas as s
import app.models as m

from app.utils import LoggerProxy, DatabaseProxy

delete_router = APIRouter(tags=["Required Endpoints"])


def delete_child_units(unit_model: m.ShopUnit, db: Session, log: logging.Logger) -> None:
    log.debug(f"deleting entity: id={unit_model.id}")

    for child_unit in unit_model.children:
        delete_child_units(child_unit, db, log)

    db.delete(unit_model)


@delete_router.delete("/delete/{id}")
async def delete_unit(id: UUID, db: Session = Depends(DatabaseProxy), log: logging.Logger = Depends(LoggerProxy)):
    log.info(f"got delete request: {id=}")

    unit_model = db.query(m.ShopUnit).get(str(id))
    if unit_model is None:
        error = s.Error(code=404, message="Item not found")
        return Response(content=error.json(), status_code=404, headers={
            "Content-Type": "application/json",
        })

    delete_child_units(unit_model, db, log)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)
