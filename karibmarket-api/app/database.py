from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Annonce(Base):
    __tablename__ = "annonces"

    id = Column(Integer, primary_key=True)
    titre = Column(String)
    prix = Column(Float)
    commune = Column(String)