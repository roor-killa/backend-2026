from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Annonce(Base):
    __tablename__ = "annonces"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    prix = Column(Float, nullable=False)
    commune = Column(String(100), nullable=False)
    categorie = Column(String(50), default="autre", nullable=False)
    actif = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Clé étrangère vers Utilisateur
    proprietaire_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)

    # Relation : accès à l'objet Utilisateur depuis une annonce
    proprietaire = relationship("Utilisateur", back_populates="annonces")
