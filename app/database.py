from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Création du moteur (le pont entre FastAPI et PostgreSQL)
engine = create_engine(settings.DATABASE_URL)

# Création des sessions (pour faire des requêtes)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour créer nos futurs modèles (tables)
Base = declarative_base()

# Fonction pour récupérer la base de données dans nos routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()