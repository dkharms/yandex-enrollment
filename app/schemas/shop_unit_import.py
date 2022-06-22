import typing as t

from enum import Enum
from uuid import UUID
from datetime import datetime

from .shop_unit import ShopUnitType

from pydantic import BaseModel, Field


class ShopUnitImport(BaseModel):
    id: UUID = Field(description="Unique identifier.")
    name: str = Field(description="Category or product name.")
    parentId: t.Union[None, UUID] = Field(description="Id of parent category.")
    type: ShopUnitType = Field(description="Product or category type.")
    price: t.Union[None, int] = Field(description="Average price for category or price of product.")

class ShopUnitImportRequest(BaseModel):
    items: t.List[ShopUnitImport] = Field(description="List of products and categories.")
    updateDate: datetime = Field(description="Update datetime.")
