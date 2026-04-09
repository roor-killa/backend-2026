from pydantic import BaseModel, EmailStr, Field
from app.schemas.annonce import AnnonceResponse
from typing import List, Optional


class UtilisateurBase(BaseModel):
    nom: str = Field(..., min_length=2, max_length=50)
    email: EmailStr  # Validation email automatique (pip install email-validator)
    telephone: Optional[str] = Field(None, pattern=r"^\+596\d{9}$")  # Format Martinique

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str = Field(..., min_length=8)

class UtilisateurResponse(UtilisateurBase):
    id: int
    actif: bool
    # Relation : liste des annonces de cet utilisateur
    annonces: List[AnnonceResponse] = []

    class Config:
        from_attributes = True