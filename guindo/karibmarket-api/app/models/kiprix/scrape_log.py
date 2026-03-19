from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.kiprix_database import KiprixBase


class ScrapeLog(KiprixBase):

    __tablename__ = "scrape_logs"

    id = Column(Integer, primary_key=True, index=True)
    territory = Column(String(10), nullable=False)
    pages = Column(Integer, default=1)
    status = Column(String(20), default="running")  # running, success, error
    nb_produits = Column(Integer, default=0)
    message = Column(Text, nullable=True)
    started_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)
