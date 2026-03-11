from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.annonce import AnnonceResponse


class UtilisateurBase(BaseModel):
    nom: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Nom affiche de l'utilisateur",
        examples=["Marie Louise"],
    )
    email: EmailStr = Field(..., description="Adresse email valide", examples=["marie@example.com"])
    telephone: Optional[str] = Field(
        default=None,
        pattern=r"^\+596\d{9}$",
        description="Numero au format Martinique (+596XXXXXXXXX)",
        examples=["+596696123456"],
    )


class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str = Field(
        ...,
        min_length=8,
        description="Mot de passe en clair cote entree uniquement",
        examples=["Secret123!"],
    )


class UtilisateurUpdate(BaseModel):
    nom: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Nom affiche de l'utilisateur",
    )
    email: Optional[EmailStr] = Field(default=None, description="Adresse email valide")
    telephone: Optional[str] = Field(
        default=None,
        pattern=r"^\+596\d{9}$",
        description="Numero au format Martinique (+596XXXXXXXXX)",
    )
    mot_de_passe: Optional[str] = Field(
        default=None,
        min_length=8,
        description="Mot de passe en clair cote entree uniquement",
    )
    actif: Optional[bool] = Field(default=None)


class UtilisateurResponse(UtilisateurBase):
    id: int = Field(..., examples=[1])
    actif: bool = Field(default=True, examples=[True])
    annonces: List[AnnonceResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
