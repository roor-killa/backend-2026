from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import db_dependency
from app.db.models.player_stat import PlayerStat
from app.db.models.score import Score
from app.db.models.user import User
from app.schemas.score import ScoreSubmitRequest

router = APIRouter(prefix="/scores", tags=["scores"])


@router.post("/submit")
def submit_score(payload: ScoreSubmitRequest, db: Session = Depends(db_dependency)) -> dict[str, str]:
    user = db.scalar(select(User).where(User.id == payload.user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    score = Score(user_id=payload.user_id, value=payload.value, combo_max=payload.combo_max)
    db.add(score)

    stat = db.scalar(select(PlayerStat).where(PlayerStat.user_id == payload.user_id))
    if stat is None:
        stat = PlayerStat(user_id=payload.user_id, games_played=1, best_score=payload.value)
        db.add(stat)
    else:
        stat.games_played += 1
        stat.best_score = max(stat.best_score, payload.value)

    db.commit()
    return {"message": "score submitted"}
