from pydantic import BaseModel
from typing import Optional

class Annonce(BaseModel):
    id: Optional[int] = None
    titre: str
    description: str
    prix: float
    commune: str
    categorie: str