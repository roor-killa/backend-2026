from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.core.constants import ShotResult


class Shot(Base):
    __tablename__ = "shots"

    id         = Column(Integer, primary_key=True, index=True)
    game_id    = Column(Integer, ForeignKey("games.id"),   nullable=False)
    player_id  = Column(Integer, ForeignKey("players.id"), nullable=False)

    # Coordonnées de la case visée (0 à 9)
    row        = Column(Integer, nullable=False)
    col        = Column(Integer, nullable=False)

    # Résultat : "miss" | "hit" | "sunk"
    result     = Column(String(10), nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # ── Relations ──────────────────────────────────────
    game   = relationship("Game",   back_populates="shots")
    player = relationship("Player", back_populates="shots")

    def __repr__(self):
        return f"<Shot id={self.id} [{self.row},{self.col}] result={self.result}>"