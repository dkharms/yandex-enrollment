import typing as t

from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.shop_unit import ShopUnitType, convert_datatime_to_valid_format


class ShopUnitStatisticUnit(BaseModel):
    id: UUID = Field(description="Unique identifier.")
    name: str = Field(description="Category or product name.")
    parent_id: t.Union[None, UUID] = Field(
        description="Id of parent category.", alias="parentId"
    )
    type: ShopUnitType = Field(description="Product or category type.")
    price: t.Union[None, int] = Field(
        description="Average price for category or price of product."
    )
    date: datetime = Field(description="Update time.")

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: convert_datatime_to_valid_format
        }


class ShopUnitStatisticResponse(BaseModel):
    items: t.List[ShopUnitStatisticUnit] = Field(
        description="Offers with updated prices"
    )
