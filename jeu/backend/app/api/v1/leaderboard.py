from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import db_dependency
from app.db.models.score import Score
from app.db.models.user import User

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


def _top_scores(db: Session, limit: int = 20) -> list[dict[str, int | str]]:
    rows = db.execute(
        select(User.username, Score.value)
        .join(Score, Score.user_id == User.id)
        .order_by(Score.value.desc())
        .limit(limit)
    ).all()
    return [{"username": username, "score": value} for username, value in rows]


@router.get("/global")
def global_leaderboard(db: Session = Depends(db_dependency)) -> dict[str, list[dict[str, int | str]]]:
    return {"items": _top_scores(db)}


@router.get("/weekly")
def weekly_leaderboard(db: Session = Depends(db_dependency)) -> dict[str, list[dict[str, int | str]]]:
    return {"items": _top_scores(db)}
