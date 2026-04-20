from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base de données principale (KaribMarket)
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/karibmarket"

    # Base de données Kiprix (produits scrapés par le projet POO)
    KIPRIX_DATABASE_URL: str = "postgresql://laravel:secret@localhost:5432/kiprix_db"

    # Service scraper (projet POO exposé comme API)
    SCRAPER_API_URL: str = "http://scraper-api:8090"

    # JWT
    SECRET_KEY: str = "changez-moi-en-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()