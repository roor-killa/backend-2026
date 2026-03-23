from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class CategorieAnnonce(str, Enum):
    alimentaire = "alimentaire"
    services = "services"
    loisirs = "loisirs"
    immobilier = "immobilier"
    vehicules = "vehicules"
    autre = "autre"

class AnnonceBase(BaseModel):
    titre: str = Field(..., min_length=5)
    description: Optional[str] = None
    prix: float = Field(..., gt=0)
    commune: str
    categorie: CategorieAnnonce

class AnnonceCreate(AnnonceBase):
    pass

class AnnonceUpdate(BaseModel):
    titre: Optional[str] = Field(None, min_length=5)
    prix: Optional[float] = Field(None, gt=0)
    commune: Optional[str] = None
    categorie: Optional[CategorieAnnonce] = None

class AnnonceResponse(AnnonceBase):
    id: int