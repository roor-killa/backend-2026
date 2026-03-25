from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    KIPRIX_DATABASE_URL: str

    REDIS_URL: str = "redis://localhost:6379"        # ← nouveau
    SCRAPER_PATH: str = ""                           # ← nouveau
    SCRAPER_PYTHON: str = "python" 
    class Config:
        env_file = ".env"

settings = Settings()