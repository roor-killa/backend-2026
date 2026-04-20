from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ScrapeUrlCreate(BaseModel):
    url: str
    label: Optional[str] = None


class ScrapeUrlUpdate(BaseModel):
    actif: Optional[bool] = None
    label: Optional[str] = None


class ScrapeUrlResponse(BaseModel):
    id: int
    url: str
    label: Optional[str]
    actif: bool
    created_at: Optional[datetime]
    last_scraped_at: Optional[datetime]
    nb_donnees: int

    model_config = {"from_attributes": True}
