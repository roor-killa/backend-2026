from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

# Enumération pour forcer le choix de la catégorie
class CategorieAnnonce(str, Enum):
    ALIMENTAIRE = "alimentaire"
    SERVICES = "services"
    LOISIRS = "loisirs"
    IMMOBILIER = "immobilier"
    VEHICULES = "vehicules"
    AUTRE = "autre"


class AnnonceBase(BaseModel):
    titre: str = Field(..., min_length=5, max_length=100, example="Vente de mangues Julie bio")
    description: Optional[str] = Field(None, max_length=1000)
    prix: float = Field(..., gt=0, example=3.50)  # gt=0 signifie "Greater Than 0" (positif)
    commune: str = Field(..., example="Le Lamentin")
    categorie: CategorieAnnonce = CategorieAnnonce.AUTRE

    # Validateur personnalisé pour interdire les titres composés uniquement d'espaces
    @validator("titre")
    def titre_ne_peut_pas_etre_vide(cls, v):
        if v.strip() == "":
            raise ValueError("Le titre ne peut pas être vide")
        return v.strip()

# Schéma pour CRÉER 
class AnnonceCreate(AnnonceBase):
    pass 

# Schéma pour MODIFIER 
class AnnonceUpdate(BaseModel):
    titre: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = None
    prix: Optional[float] = Field(None, gt=0)
    commune: Optional[str] = None
    categorie: Optional[CategorieAnnonce] = None

# Schéma pour la RÉPONSE (Sortie)
class AnnonceResponse(AnnonceBase):
    id: int
    actif: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True