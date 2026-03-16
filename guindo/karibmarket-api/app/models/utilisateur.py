from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Utilisateur(Base):

    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)

    nom = Column(String(50), nullable=False)

    email = Column(String(100), unique=True, index=True)

    telephone = Column(String(20))

    hashed_password = Column(String(255))

    actif = Column(Boolean, default=True)

    annonces = relationship("Annonce", back_populates="proprietaire")