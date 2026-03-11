from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from app.schemas.annonce import AnnonceResponse

class UtilisateurBase(BaseModel):
    nom: str = Field(..., min_length=2, max_length=50)
    email: EmailStr  
    telephone: Optional[str] = Field(None, pattern=r"^\+596\d{9}$")  

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str = Field(..., min_length=8)

class UtilisateurResponse(UtilisateurBase):
    id: int
    actif: bool
    annonces: List[AnnonceResponse] = []

    class Config:
        from_attributes = True