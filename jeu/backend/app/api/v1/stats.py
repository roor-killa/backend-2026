from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import db_dependency
from app.db.models.player_stat import PlayerStat

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/me")
def my_stats(
    user_id: int = Query(..., ge=1),
    db: Session = Depends(db_dependency),
) -> dict[str, int]:
    stat = db.scalar(select(PlayerStat).where(PlayerStat.user_id == user_id))
    if stat is None:
        raise HTTPException(status_code=404, detail="Stats not found")

    return {
        "games_played": stat.games_played,
        "best_score": stat.best_score,
    }
