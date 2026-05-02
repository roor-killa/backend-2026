from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..schemas.score import LeaderboardEntry
from ..services.score_service import ScoreService

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=list[LeaderboardEntry])
async def get_leaderboard(limit: int = Query(default=10, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    service = ScoreService(db)
    return await service.get_leaderboard(limit)
