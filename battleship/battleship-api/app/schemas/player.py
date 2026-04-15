from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# ── Création d'un joueur (données envoyées par le client) ──
class PlayerCreate(BaseModel):
    pseudo: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Pseudo unique du joueur (3 à 50 caractères)"
    )

    @field_validator("pseudo")
    @classmethod
    def pseudo_must_be_alphanumeric(cls, v: str) -> str:
        """Le pseudo ne doit contenir que des lettres, chiffres et underscores."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Le pseudo ne doit contenir que des lettres, chiffres, - ou _")
        return v.strip()


# ── Réponse complète d'un joueur (données renvoyées par l'API) ──
class PlayerResponse(BaseModel):
    id:           int
    pseudo:       str
    score:        int
    games_played: int
    created_at:   datetime

    # Permet à Pydantic de lire les attributs d'un objet SQLAlchemy
    model_config = {"from_attributes": True}


# ── Entrée du leaderboard ──
class LeaderboardEntry(BaseModel):
    rank:         int
    id:           int
    pseudo:       str
    score:        int
    games_played: int

    model_config = {"from_attributes": True}