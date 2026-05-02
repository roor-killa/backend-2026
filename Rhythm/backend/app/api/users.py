from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..schemas.user import UserCreate, UserLogin, UserResponse
from ..services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.create_user(data)
    return user


@router.post("/login", response_model=UserResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.authenticate_user(data.username, data.password)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    return user


@router.post("/{user_id}/shields/consume", response_model=UserResponse)
async def consume_shield(user_id: str, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.consume_shield(user_id)
    return user


@router.get("/{user_id}/best-score")
async def get_best_score(user_id: str, db: AsyncSession = Depends(get_db)):
    from ..services.score_service import ScoreService
    service = ScoreService(db)
    best = await service.get_user_best_score(user_id)
    return {"best_score": best}
