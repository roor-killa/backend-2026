
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class CategorieEnum(enum.Enum):
    alimentaire = "alimentaire"
    services = "services"
    loisirs = "loisirs"
    immobilier = "immobilier"
    vehicules = "vehicules"
    autre = "autre"

class Annonce(Base):
    __tablename__ = "annonces"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    prix = Column(Float, nullable=False)
    commune = Column(String(50), nullable=False)
    categorie = Column(SAEnum(CategorieEnum), default=CategorieEnum.autre)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Clé étrangère vers l'utilisateur propriétaire
    proprietaire_id = Column(Integer, ForeignKey("utilisateurs.id"))
    proprietaire = relationship("Utilisateur", back_populates="annonces")