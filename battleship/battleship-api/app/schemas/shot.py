from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from app.core.constants import GRID_SIZE


# ── Effectuer un tir ──────────────────────────────────
class ShotCreate(BaseModel):
    player_id: int = Field(..., description="ID du joueur qui tire")
    row: int = Field(..., ge=0, lt=GRID_SIZE, description="Ligne visée (0-9)")
    col: int = Field(..., ge=0, lt=GRID_SIZE, description="Colonne visée (0-9)")


# ── Réponse après un tir ──────────────────────────────
class ShotResponse(BaseModel):
    id:         int
    game_id:    int
    player_id:  int
    row:        int
    col:        int
    result:     str          # "miss" | "hit" | "sunk"
    created_at: datetime

    # Infos supplémentaires utiles pour Unity WebGL
    game_over:  bool = False  # True si ce tir a terminé la partie
    winner_id:  int | None = None

    model_config = {"from_attributes": True}


# ── Historique des tirs ───────────────────────────────
class ShotHistoryResponse(BaseModel):
    shots: list[ShotResponse]
    total: int