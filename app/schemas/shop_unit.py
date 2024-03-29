import typing as t

from enum import Enum
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


def convert_datatime_to_valid_format(dt: datetime) -> str:
    return f"{dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z"


class ShopUnitType(str, Enum):
    offer = "OFFER"
    category = "CATEGORY"


class ShopUnit(BaseModel):
    id: UUID = Field(description="Unique identifier.")
    name: str = Field(description="Category or product name.")
    date: datetime = Field(description="Update time.")
    parent_id: t.Union[None, UUID] = Field(
        description="Id of parent category.", alias="parentId"
    )
    type: ShopUnitType = Field(description="Product or category type.")
    price: t.Union[None, int] = Field(
        description="Average price for category or price of product."
    )
    children: t.Union[None, t.List["ShopUnit"]] = Field(
        description="List of products for category."
    )

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: convert_datatime_to_valid_format
        }
