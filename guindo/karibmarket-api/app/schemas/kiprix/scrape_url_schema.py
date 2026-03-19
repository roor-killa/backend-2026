from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class ScrapeUrlCreate(BaseModel):
    url: HttpUrl
    label: Optional[str] = None


class ScrapeUrlUpdate(BaseModel):
    label: Optional[str] = None
    actif: Optional[bool] = None


class ScrapeUrlResponse(BaseModel):
    id: int
    url: str
    label: Optional[str] = None
    actif: bool
    created_at: Optional[datetime] = None
    last_scraped_at: Optional[datetime] = None
    nb_donnees: int

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_urls: int
    urls_actives: int
    total_donnees: int
    derniere_maj: Optional[datetime] = None
