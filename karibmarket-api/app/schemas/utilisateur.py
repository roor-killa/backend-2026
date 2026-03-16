from pydantic import BaseModel, EmailStr
from typing import Optional


class UtilisateurBase(BaseModel):
    nom: str
    email: EmailStr
    telephone: Optional[str] = None


class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str


class UtilisateurResponse(UtilisateurBase):
    id: int
    actif: bool
