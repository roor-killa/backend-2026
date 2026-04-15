from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings
from functools import lru_cache


# ── Configuration (lit le fichier .env) ───────────────
class Settings(BaseSettings):
    database_url: str = "sqlite:///./battleship.db"
    secret_key: str = "dev_secret_key"
    debug: bool = True
    allowed_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Retourne les settings en cache (lus une seule fois)."""
    return Settings()


# ── Moteur SQLAlchemy ──────────────────────────────────
def get_engine():
    settings = get_settings()
    db_url = settings.database_url

    # SQLite nécessite un argument supplémentaire pour le multithreading
    if db_url.startswith("sqlite"):
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False}
        )
    # PostgreSQL : connexion standard
    return create_engine(db_url)


engine = get_engine()

# ── Session factory ────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ── Classe de base pour tous les modèles ──────────────
class Base(DeclarativeBase):
    pass


# ── Dépendance FastAPI (injection dans les routers) ───
def get_db():
    """
    Fournit une session BDD pour chaque requête.
    La session est fermée automatiquement après la requête.

    Utilisation dans un router :
        def mon_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Création des tables au démarrage ──────────────────
def create_tables():
    """Crée toutes les tables si elles n'existent pas encore."""
    Base.metadata.create_all(bind=engine)