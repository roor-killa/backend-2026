from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    telephone = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)  # On ne stockera jamais le mot de passe en clair !
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relation : un utilisateur peut avoir plusieurs annonces
    annonces = relationship("Annonce", back_populates="proprietaire")