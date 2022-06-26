import typing as t

from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, validator

from app.schemas.shop_unit import ShopUnitType, convert_datatime_to_valid_format


class ShopUnitImport(BaseModel):
    id: UUID = Field(description="Unique identifier.")
    name: str = Field(description="Category or product name.")
    parent_id: t.Union[None, UUID] = Field(
        description="Id of parent category.", alias="parentId"
    )
    type: ShopUnitType = Field(description="Product or category type.")
    price: t.Union[None, int] = Field(
        description="Average price for category or price of product."
    )

    @validator("price")
    def validate_price(cls, price, values):
        if values["type"] == ShopUnitType.category and price != None:
            raise ValueError("Category must have null price!")
        if values["type"] == ShopUnitType.offer and (price is None or price < 0):
            raise ValueError("Product price must be >= 0!")
        return price


class ShopUnitImportRequest(BaseModel):
    items: t.List[ShopUnitImport] = Field(
        description="List of products and categories."
    )
    update_date: datetime = Field(
        description="Update datetime.", alias="updateDate",
    )

    @validator("update_date")
    def validate_update_date(cls, update_date):
        try:
            datetime.strptime(update_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e:
            raise ValueError("Wrong update date format!")
        finally:
            return update_date

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: convert_datatime_to_valid_format
        }
