from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ScrapeRunRequest(BaseModel):
    territory: str
    pages: int = 1


class ScrapeLogResponse(BaseModel):
    id: int
    territory: str
    pages: int
    status: str  # running | success | error
    nb_produits: int
    message: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

    model_config = {"from_attributes": True}
