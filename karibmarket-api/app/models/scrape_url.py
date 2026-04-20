from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class ScrapeUrl(Base):
    __tablename__ = "scrape_urls"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    label = Column(String, nullable=True)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)
    nb_donnees = Column(Integer, default=0)
