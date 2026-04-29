"""
Ti Punch Master — Modèles Pydantic
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional


class ScoreRequest(BaseModel):
    client_id: str = Field(..., example="marie_helene")
    cocktail:  str = Field(..., example="tipunch")
    dosages:   Dict[str, float] = Field(
        ..., example={"rhum": 5.0, "citron": 3.0, "sucre": 2.0}
    )

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "marie_helene",
                "cocktail":  "tipunch",
                "dosages":   {"rhum": 5, "citron": 3, "sucre": 2}
            }
        }


class ScoreResponse(BaseModel):
    score:      int
    feedback:   str
    target:     Dict[str, float]
    diffs:      Dict[str, float]
    total_diff: float


class LeaderboardEntry(BaseModel):
    player_name: str
    score:       int
    date:        str
    timestamp:   Optional[str] = None


class LeaderboardPost(BaseModel):
    player_name: str = Field(..., example="Barman")
    score:       int  = Field(..., ge=0, le=500, example=320)

    class Config:
        json_schema_extra = {
            "example": {
                "player_name": "Barman",
                "score": 320
            }
        }
