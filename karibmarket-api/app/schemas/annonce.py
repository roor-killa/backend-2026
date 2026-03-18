from pydantic import BaseModel, Field

class AnnonceCreate(BaseModel):
    titre: str = Field(min_length=3)
    prix: float = Field(gt=0)