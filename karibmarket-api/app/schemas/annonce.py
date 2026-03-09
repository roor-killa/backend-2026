from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


# Enum pour les catégories d'annonces
class CategorieAnnonce(str, Enum):
    ALIMENTAIRE = "alimentaire"
    SERVICES = "services"
    LOISIRS = "loisirs"
    IMMOBILIER = "immobilier"
    VEHICULES = "vehicules"
    AUTRE = "autre"


# Schéma de BASE — champs communs
class AnnonceBase(BaseModel):
    titre: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Titre de l'annonce",
        example="Vente de mangues Julie bio"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Description détaillée"
    )
    prix: float = Field(
        ...,
        gt=0,
        description="Prix en euros, doit être positif",
        example=3.50
    )
    commune: str = Field(
        ...,
        description="Commune en Martinique ou Guadeloupe",
        example="Le Lamentin"
    )
    categorie: CategorieAnnonce = CategorieAnnonce.AUTRE

    # Validateur personnalisé (syntaxe Pydantic v2)
    @field_validator("titre")
    @classmethod
    def titre_ne_peut_pas_etre_vide(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("Le titre ne peut pas être vide ou contenir uniquement des espaces")
        return v.strip()  # On nettoie les espaces en bord


# Schéma pour la CRÉATION (entrée)
class AnnonceCreate(AnnonceBase):
    pass  # Hérite tout de AnnonceBase


# Schéma pour la MISE À JOUR partielle (PATCH)
class AnnonceUpdate(BaseModel):
    titre: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = None
    prix: Optional[float] = Field(None, gt=0)
    commune: Optional[str] = None
    categorie: Optional[CategorieAnnonce] = None
    # Tous les champs sont optionnels pour le PATCH


# Schéma pour la RÉPONSE (sortie) — inclut les champs serveur
class AnnonceResponse(AnnonceBase):
    id: int
    actif: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # Permet la conversion depuis un objet SQLAlchemy
