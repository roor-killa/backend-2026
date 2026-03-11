 
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Création du moteur de connexion
engine = create_engine(settings.DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour tous les modèles
Base = declarative_base()

# Dépendance FastAPI — injecte une session dans chaque requête
def get_db():
    db = SessionLocal()
    try:
        yield db  # Fournit la session
    finally:
        db.close()  # Ferme TOUJOURS la session après la requête