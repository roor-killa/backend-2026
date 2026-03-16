from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Champs communs
class AnnonceBase(BaseModel):
    titre: str = Field(..., min_length=5, max_length=100)
    description: Optional[str] = None
    prix: float = Field(..., gt=0)
    commune: str
    categorie: str


# Création annonce
class AnnonceCreate(AnnonceBase):
    pass


# Modification annonce
class AnnonceUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    prix: Optional[float] = None
    commune: Optional[str] = None
    categorie: Optional[str] = None


# Réponse API
class AnnonceResponse(AnnonceBase):
    id: int
    created_at: datetime
