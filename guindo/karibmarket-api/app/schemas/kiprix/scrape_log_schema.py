from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ScrapeLogResponse(BaseModel):
    id: int
    territory: str
    pages: int
    status: str
    nb_produits: int
    message: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ScrapeRunRequest(BaseModel):
    territory: str = "mq"
    pages: int = 1
