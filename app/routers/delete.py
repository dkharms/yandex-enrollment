import typing as t

from uuid import UUID
from logging import Logger

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

import app.schemas as s
import app.models as m

from app.utils import LoggerProxy, DatabaseProxy

delete_router = APIRouter(tags=["Must Have Endpoints"])


def delete_child_entities(item: m.ShopUnit, db: Session, log: Logger) -> None:
    log.info(f"deleting entity: id={item.id}")

    for child_item in item.children:
        delete_child_entities(child_item, db, log)

    db.delete(item)
    db.commit()


@delete_router.delete("/delete/{id}")
def delete_entity(id: UUID, db: Session = Depends(DatabaseProxy), log: Logger = Depends(LoggerProxy)):
    log.info(f"got request for deleting entity: id={id}")

    item_model = db.query(m.ShopUnit).get(str(id))
    if item_model is None:
        error = s.Error(code=404, message="Item not found")
        return Response(content=error.json(), status_code=404)

    delete_child_entities(item_model, db, log)

    return Response(status_code=status.HTTP_200_OK)
