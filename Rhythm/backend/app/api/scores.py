from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..schemas.score import ScoreCreate, ScoreResponse
from ..services.score_service import ScoreService

router = APIRouter(prefix="/scores", tags=["scores"])


@router.post("", response_model=ScoreResponse, status_code=201)
async def submit_score(data: ScoreCreate, db: AsyncSession = Depends(get_db)):
    service = ScoreService(db)
    score = await service.submit_score(data)
    return score
