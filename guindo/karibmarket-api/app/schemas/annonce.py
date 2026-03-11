from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class CategorieAnnonce(str, Enum):
    ALIMENTAIRE = "alimentaire"
    SERVICES = "services"
    LOISIRS = "loisirs"
    IMMOBILIER = "immobilier"
    VEHICULES = "vehicules"
    AUTRE = "autre"

class AnnonceBase(BaseModel):
    titre: str = Field(..., min_length=5, max_length=100)
    description: Optional[str] = None
    prix: float = Field(..., gt=0)
    commune: str
    categorie: CategorieAnnonce

class AnnonceCreate(AnnonceBase):
    pass

class AnnonceUpdate(BaseModel):
    titre: Optional[str] = Field(None, min_length=5)
    description: Optional[str] = None
    prix: Optional[float] = Field(None, gt=0)
    commune: Optional[str] = None
    categorie: Optional[CategorieAnnonce] = None

class AnnonceResponse(AnnonceBase):
    id: int
    actif: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True