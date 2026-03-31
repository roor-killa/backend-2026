from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class CategorieAnnonce(str, Enum):
    alimentaire = "alimentaire"
    services = "services"
    loisirs = "loisirs"
    immobilier = "immobilier"
    vehicules = "vehicules"
    autre = "autre"


class AnnonceBase(BaseModel):
    titre: str = Field(..., min_length=5, max_length=100, example="Vente mangues bio")
    description: Optional[str] = Field(None, max_length=1000)
    prix: float = Field(..., gt=0, example=3.5)
    commune: str = Field(..., example="Le Lamentin")
    categorie: CategorieAnnonce = CategorieAnnonce.autre

    @field_validator("titre")
    def titre_valide(cls, v):
        if v.strip() == "":
            raise ValueError("Le titre ne peut pas être vide")
        return v.strip()


class AnnonceCreate(AnnonceBase):
    pass


class AnnonceUpdate(BaseModel):
    titre: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = None
    prix: Optional[float] = Field(None, gt=0)
    commune: Optional[str] = None
    categorie: Optional[CategorieAnnonce] = None


class AnnonceResponse(AnnonceBase):
    id: int
    actif: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True