from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str = "change-me"
    debug: bool = False

    shield_price: int = 100
    perfect_hit_funds: int = 15
    good_hit_funds: int = 10
    bad_hit_funds: int = 5

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    class Config:
        env_file = ".env"


settings = Settings()
