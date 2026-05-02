import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from ..models.score import Score
from ..models.user import User
from ..schemas.score import ScoreCreate, LeaderboardEntry
from ..utils.exceptions import UserNotFoundError


class ScoreService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit_score(self, data: ScoreCreate) -> Score:
        # Update funds and verify user exists in one query
        funds_result = await self.db.execute(
            update(User)
            .where(User.id == data.user_id)
            .values(account_funds=User.account_funds + data.funds_earned)
            .returning(User.id)
        )
        if not funds_result.scalar_one_or_none():
            raise UserNotFoundError(f"User '{data.user_id}' not found")

        score = Score(
            id=str(uuid.uuid4()),
            user_id=data.user_id,
            score=data.score,
        )
        self.db.add(score)
        await self.db.flush()
        return score

    async def get_leaderboard(self, limit: int = 10) -> list[LeaderboardEntry]:
        result = await self.db.execute(
            select(Score, User.username)
            .join(User, Score.user_id == User.id)
            .order_by(desc(Score.score))
            .limit(limit)
        )
        return [LeaderboardEntry(username=username, score=score.score) for score, username in result.all()]

    async def get_user_best_score(self, user_id: str) -> int | None:
        result = await self.db.execute(
            select(Score.score).where(Score.user_id == user_id).order_by(desc(Score.score)).limit(1)
        )
        row = result.scalar_one_or_none()
        return row

    async def get_user_score_history(self, user_id: str) -> list[Score]:
        result = await self.db.execute(
            select(Score).where(Score.user_id == user_id).order_by(desc(Score.achieved_at))
        )
        return list(result.scalars().all())
