import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    account_funds: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    shields_owned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    scores: Mapped[list["Score"]] = relationship("Score", back_populates="user", cascade="all, delete-orphan")
    purchases: Mapped[list["Purchase"]] = relationship("Purchase", back_populates="user", cascade="all, delete-orphan")
