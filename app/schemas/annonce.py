from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategorieAnnonce(str, Enum):
    ALIMENTAIRE = "alimentaire"
    SERVICES = "services"
    LOISIRS = "loisirs"
    IMMOBILIER = "immobilier"
    VEHICULES = "vehicules"
    AUTRE = "autre"


class AnnonceBase(BaseModel):
    titre: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Titre de l'annonce",
        examples=["Vente de mangues Julie bio"],
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Description detaillee de l'annonce",
        examples=["Mangues fraichement recoltees, lot de 5 kg."],
    )
    prix: float = Field(
        ...,
        gt=0,
        description="Prix en euros, doit etre positif",
        examples=[3.5],
    )
    commune: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Commune en Martinique ou Guadeloupe",
        examples=["Le Lamentin"],
    )
    categorie: CategorieAnnonce = Field(
        default=CategorieAnnonce.AUTRE,
        description="Categorie de l'annonce",
        examples=["alimentaire"],
    )

    @field_validator("titre")
    @classmethod
    def valider_titre(cls, value: str) -> str:
        titre = value.strip()
        if not titre:
            raise ValueError("Le titre ne peut pas etre vide ou compose d'espaces")
        return titre


class AnnonceCreate(AnnonceBase):
    pass


class AnnonceUpdate(BaseModel):
    titre: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    prix: Optional[float] = Field(None, gt=0)
    commune: Optional[str] = Field(None, min_length=2, max_length=100)
    categorie: Optional[CategorieAnnonce] = None

    @field_validator("titre")
    @classmethod
    def valider_titre_update(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        titre = value.strip()
        if not titre:
            raise ValueError("Le titre ne peut pas etre vide ou compose d'espaces")
        return titre


class AnnonceResponse(AnnonceBase):
    id: int = Field(..., examples=[1])
    proprietaire_id: int = Field(..., examples=[1])
    actif: bool = Field(default=True, examples=[True])
    created_at: datetime = Field(..., examples=["2026-03-09T10:00:00"])
    updated_at: Optional[datetime] = Field(default=None, examples=["2026-03-09T11:00:00"])

    model_config = ConfigDict(from_attributes=True)
