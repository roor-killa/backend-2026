from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text
from sqlalchemy.sql import func
from app.kiprix_database import KiprixBase


class Produit(KiprixBase):

    __tablename__ = "produits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=True)
    price_france = Column(String(50), nullable=True)
    price_dom = Column(String(50), nullable=True)
    difference = Column(String(50), nullable=True)
    quantity_value = Column(Numeric(10, 4), nullable=True)
    quantity_unit = Column(String(20), nullable=True)
    unit_reference = Column(String(20), nullable=True)
    unit_price_france = Column(Numeric(10, 2), nullable=True)
    unit_price_dom = Column(Numeric(10, 2), nullable=True)
    territory = Column(String(10), nullable=True)
    territory_name = Column(String(100), nullable=True)
    scraped_at = Column(DateTime, server_default=func.now())
