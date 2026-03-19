from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.kiprix_database import KiprixBase


class ScrapeUrl(KiprixBase):

    __tablename__ = "scrape_urls"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, nullable=False, unique=True)
    label = Column(String(100), nullable=True)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_scraped_at = Column(DateTime, nullable=True)
    nb_donnees = Column(Integer, default=0)
