import logging
import typing as t

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status, Response
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND

import app.schemas as s
import app.models as m

from app.utils import LoggerProxy, DatabaseProxy, ConfigProxy

delete_router = APIRouter(tags=["Must Have Endpoints"])


def delete_entities(item: m.ShopUnit, db: Session):
    for child_item in item.children:
        delete_entities(child_item, db)

    db.delete(item)
    db.commit()


@delete_router.delete("/delete/{id}")
def delete_entity(id: UUID, db: Session = Depends(DatabaseProxy)):
    item_model = db.query(m.ShopUnit).get(str(id))
    if item_model is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    delete_entities(item_model, db)

    return Response(status_code=status.HTTP_200_OK)
