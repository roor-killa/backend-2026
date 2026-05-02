from datetime import datetime
from pydantic import BaseModel


class ScoreCreate(BaseModel):
    user_id: str
    score: int
    funds_earned: float


class ScoreResponse(BaseModel):
    id: str
    user_id: str
    score: int
    achieved_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    username: str
    score: int
