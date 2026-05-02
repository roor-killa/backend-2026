import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ..models.user import User
from ..schemas.user import UserCreate
from ..utils.security import hash_password, verify_password
from ..utils.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
    InsufficientShieldsError,
)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, data: UserCreate) -> User:
        result = await self.db.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none():
            raise UserAlreadyExistsError(f"Username '{data.username}' is already taken")

        user = User(
            id=str(uuid.uuid4()),
            username=data.username,
            password_hash=await hash_password(data.password),
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def authenticate_user(self, username: str, password: str) -> User:
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user or not await verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid username or password")
        return user

    async def get_user_by_id(self, user_id: str) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError(f"User '{user_id}' not found")
        return user

    async def update_funds(self, user_id: str, amount: float) -> User:
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(account_funds=User.account_funds + amount)
            .returning(User)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError(f"User '{user_id}' not found")
        return user

    async def update_shields(self, user_id: str, delta: int) -> User:
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(shields_owned=User.shields_owned + delta)
            .returning(User)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError(f"User '{user_id}' not found")
        return user

    async def consume_shield(self, user_id: str) -> User:
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id, User.shields_owned > 0)
            .values(shields_owned=User.shields_owned - 1)
            .returning(User)
        )
        user = result.scalar_one_or_none()
        if not user:
            check = await self.db.execute(
                select(User.shields_owned).where(User.id == user_id)
            )
            shields = check.scalar_one_or_none()
            if shields is None:
                raise UserNotFoundError(f"User '{user_id}' not found")
            raise InsufficientShieldsError("No shields available to consume")
        return user
