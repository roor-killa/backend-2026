from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.schemas.annonce import CategorieAnnonce


class Annonce(Base):
    __tablename__ = "annonces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    titre: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    prix: Mapped[float] = mapped_column(Float, nullable=False)
    commune: Mapped[str] = mapped_column(String(100), nullable=False)
    categorie: Mapped[CategorieAnnonce] = mapped_column(
        SAEnum(
            CategorieAnnonce,
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=CategorieAnnonce.AUTRE,
        nullable=False,
    )
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    proprietaire_id: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id"), nullable=False)
    proprietaire = relationship("Utilisateur", back_populates="annonces")
