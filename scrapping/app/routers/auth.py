from pydantic import BaseModel, EmailStr, Field
from typing import List

class UtilisateurBase(BaseModel):
    nom: str = Field(...,min_length=2,max_length=20)
    email: EmailStr
    telephone: Optional[str] = Field(None, pattern=r"^\+596\d{9}$") 

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str = Field(...,min_length=8)
