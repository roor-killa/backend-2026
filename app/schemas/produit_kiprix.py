from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProduitKiprixResponse(BaseModel):
    id: int
    name: str = Field(..., examples=["Riz basmati 1kg"])
    url: str
    price_france: str | None = None
    price_dom: str | None = None
    difference: str | None = None
    quantity_value: float | None = None
    quantity_unit: str | None = None
    unit_reference: str | None = None
    unit_price_france: float | None = None
    unit_price_dom: float | None = None
    territory: str = Field(..., examples=["mq"])
    territory_name: str | None = Field(default=None, examples=["Martinique"])
    scraped_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProduitKiprixImportRequest(BaseModel):
    territory: str = Field(default="mq", description="Code territoire: gp, mq, re, gf")
    max_pages: int = Field(default=1, ge=1, le=20)


class ProduitKiprixImportResponse(BaseModel):
    territoire: str
    pages: int
    produits_scrapes: int
    produits_ajoutes: int
    produits_mis_a_jour: int
