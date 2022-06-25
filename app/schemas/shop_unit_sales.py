import typing as t

from pydantic import BaseModel, Field

from app.schemas import ShopUnit


class ShopUnitSales(BaseModel):
    items: t.List[ShopUnit] = Field(description="Offers with updated prices")
