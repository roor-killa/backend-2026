from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.core.constants import GRID_SIZE


def empty_grid() -> list:
    """Retourne une grille vide de GRID_SIZE x GRID_SIZE remplie de 0."""
    return [[0] * GRID_SIZE for _ in range(GRID_SIZE)]


class Board(Base):
    __tablename__ = "boards"

    id         = Column(Integer, primary_key=True, index=True)
    game_id    = Column(Integer, ForeignKey("games.id"),   nullable=False)
    player_id  = Column(Integer, ForeignKey("players.id"), nullable=False)

    # Grille JSON : tableau 10x10
    # Valeurs :
    #   0 → case vide (non jouée)
    #   1 → bateau présent (non touché)
    #   2 → touché
    #   3 → à l'eau (tir ennemi manqué)
    grid = Column(JSON, nullable=False, default=empty_grid)

    # ── Relations ──────────────────────────────────────
    game    = relationship("Game",   back_populates="boards")
    player  = relationship("Player", back_populates="boards")
    ships   = relationship("Ship",   back_populates="board", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Board id={self.id} game_id={self.game_id} player_id={self.player_id}>"