from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.core.constants import GameStatus, GameMode, Difficulty


class Game(Base):
    __tablename__ = "games"

    id            = Column(Integer, primary_key=True, index=True)

    # Mode : "solo" ou "multiplayer"
    mode          = Column(String(20), nullable=False, default=GameMode.SOLO)

    # Difficulté IA : "easy", "medium", "hard" (solo uniquement)
    difficulty    = Column(String(10), nullable=True)

    # Statut : "waiting" | "placement" | "playing" | "finished"
    status        = Column(String(20), nullable=False, default=GameStatus.PLACEMENT)

    # Joueurs de la partie
    player1_id    = Column(Integer, ForeignKey("players.id"), nullable=False)
    player2_id    = Column(Integer, ForeignKey("players.id"), nullable=True)

    # ID du joueur dont c'est le tour
    current_turn  = Column(Integer, ForeignKey("players.id"), nullable=True)

    # ID du gagnant (null tant que la partie n'est pas terminée)
    winner_id     = Column(Integer, ForeignKey("players.id"), nullable=True)

    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # ── Relations ──────────────────────────────────────
    # Une partie a deux boards (un par joueur)
    boards  = relationship("Board", back_populates="game")

    # Une partie a plusieurs tirs
    shots   = relationship("Shot",  back_populates="game")

    # Joueur dont c'est le tour
    current_player = relationship(
        "Player",
        foreign_keys=[current_turn]
    )

    # Joueur gagnant
    winner = relationship(
        "Player",
        foreign_keys=[winner_id]
    )

    def __repr__(self):
        return f"<Game id={self.id} mode={self.mode} status={self.status}>"