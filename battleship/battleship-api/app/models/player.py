from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id            = Column(Integer, primary_key=True, index=True)
    pseudo        = Column(String(50), unique=True, nullable=False, index=True)
    score         = Column(Integer, default=0, nullable=False)
    games_played  = Column(Integer, default=0, nullable=False)
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # ── Relations ──────────────────────────────────────
    # Un joueur peut avoir plusieurs boards (une par partie)
    boards = relationship("Board", back_populates="player")

    # Un joueur peut avoir effectué plusieurs tirs
    shots  = relationship("Shot", back_populates="player")

    def __repr__(self):
        return f"<Player id={self.id} pseudo={self.pseudo} score={self.score}>"