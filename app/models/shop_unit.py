from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base


from app.schemas import ShopUnitType

Base = declarative_base()


class ShopUnit(Base):
    __tablename__ = "shopunits"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    parent_id = Column(String, ForeignKey("shopunits.id"))
    type = Column(Enum(ShopUnitType))
    price = Column(Integer, nullable=True)

    parent = relationship("ShopUnit", backref="children", remote_side=[id])
