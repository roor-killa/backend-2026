from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# Moteur SQLAlchemy — se connecte à PostgreSQL via DATABASE_URL
engine = create_engine(settings.DATABASE_URL)

# Fabrique de sessions — chaque requête HTTP aura sa propre session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Classe de base pour tous les modèles ORM
class Base(DeclarativeBase):
    pass


# Dépendance FastAPI — fournit une session DB par requête, puis la ferme
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
