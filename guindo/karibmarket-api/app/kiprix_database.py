from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

KIPRIX_DATABASE_URL = os.getenv(
    "KIPRIX_DATABASE_URL",
    "postgresql://laravel:secret@localhost:5433/kiprix_db"
)

kiprix_engine = create_engine(settings.KIPRIX_DATABASE_URL)

KiprixSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=kiprix_engine
)

KiprixBase = declarative_base()


def get_kiprix_db():
    db = KiprixSessionLocal()
    try:
        yield db
    finally:
        db.close()
