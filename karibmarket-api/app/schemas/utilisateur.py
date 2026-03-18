from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    nom: str = Field(min_length=2, max_length=50)
    email: EmailStr
    telephone: str = Field(pattern=r"^\+596\d{9}$")
    mot_de_passe: str = Field(min_length=8)