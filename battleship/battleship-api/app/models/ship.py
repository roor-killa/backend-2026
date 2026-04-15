from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Ship(Base):
    __tablename__ = "ships"

    id        = Column(Integer, primary_key=True, index=True)
    board_id  = Column(Integer, ForeignKey("boards.id"), nullable=False)

    # Type : "carrier" | "cruiser" | "destroyer" | "submarine" | "torpedo"
    type      = Column(String(20), nullable=False)

    # Positions occupées : liste de [row, col]
    # Exemple : [[2,3], [2,4], [2,5]] pour un destroyer horizontal
    positions = Column(JSON, nullable=False)

    # Orientation : "horizontal" | "vertical"
    orientation = Column(String(10), nullable=False)

    # True quand toutes les cases du bateau ont été touchées
    is_sunk   = Column(Boolean, default=False, nullable=False)

    # ── Relations ──────────────────────────────────────
    board = relationship("Board", back_populates="ships")

    def __repr__(self):
        return f"<Ship id={self.id} type={self.type} is_sunk={self.is_sunk}>"