from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database_kiprix import KiprixBase


class Produit(KiprixBase):
    """Modèle ORM mappé sur la table 'produits' de kiprix_db (créée par le projet POO)."""
    __tablename__ = "produits"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    url = Column(String)
    price_france = Column(String(50))
    price_dom = Column(String(50))
    difference = Column(String(50))
    quantity_value = Column(Numeric(10, 4))
    quantity_unit = Column(String(20))
    unit_reference = Column(String(20))
    unit_price_france = Column(Numeric(10, 2))
    unit_price_dom = Column(Numeric(10, 2))
    territory = Column(String(10))
    territory_name = Column(String(100))
    scraped_at = Column(DateTime)
