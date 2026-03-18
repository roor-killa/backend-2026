from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProduitResponse(BaseModel):
    id: int
    name: str
    url: Optional[str] = None
    price_france: Optional[str] = None
    price_dom: Optional[str] = None
    difference: Optional[str] = None
    quantity_value: Optional[Decimal] = None
    quantity_unit: Optional[str] = None
    unit_reference: Optional[str] = None
    unit_price_france: Optional[Decimal] = None
    unit_price_dom: Optional[Decimal] = None
    territory: Optional[str] = None
    territory_name: Optional[str] = None
    scraped_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProduitListResponse(BaseModel):
    total: int
    page: int
    limit: int
    resultats: list[ProduitResponse]
