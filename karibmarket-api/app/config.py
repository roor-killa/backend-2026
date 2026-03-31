from pydantic_settings import BaseSettings  # pip install pydantic-settings

class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/karibmarket"

    # JWT (Module 5)
    SECRET_KEY: str = "changez-moi-en-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"  # Lire depuis le fichier .env

settings = Settings()