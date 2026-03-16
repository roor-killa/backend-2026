from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True)
    nom = Column(String)
    email = Column(String)
    telephone = Column(String)
    hashed_password = Column(String)
    actif = Column(Boolean, default=True)
