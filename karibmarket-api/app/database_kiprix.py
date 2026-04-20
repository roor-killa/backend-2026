from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

kiprix_engine = create_engine(settings.KIPRIX_DATABASE_URL)
KiprixSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=kiprix_engine)


class KiprixBase(DeclarativeBase):
    pass


def get_kiprix_db():
    db = KiprixSessionLocal()
    try:
        yield db
    finally:
        db.close()
