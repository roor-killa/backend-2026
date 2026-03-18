from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProduitKiprix(Base):
    __tablename__ = "produits_kiprix"
    __table_args__ = (
        UniqueConstraint("url", "territory", name="uq_produits_kiprix_url_territory"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    price_france: Mapped[str | None] = mapped_column(String(50), nullable=True)
    price_dom: Mapped[str | None] = mapped_column(String(50), nullable=True)
    difference: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantity_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    quantity_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    unit_reference: Mapped[str | None] = mapped_column(String(20), nullable=True)
    unit_price_france: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit_price_dom: Mapped[float | None] = mapped_column(Float, nullable=True)
    territory: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    territory_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
