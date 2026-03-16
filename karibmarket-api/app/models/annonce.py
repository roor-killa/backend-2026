from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from app.database import Base


class Annonce(Base):
    __tablename__ = "annonces"

    id = Column(Integer, primary_key=True)
    titre = Column(String)
    prix = Column(Float)
    commune = Column(String)
    categorie = Column(String)

    actif = Column(Boolean, default=True)

    proprietaire_id = Column(Integer, ForeignKey("utilisateurs.id"))
