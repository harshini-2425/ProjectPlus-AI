import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL") or (
        "sqlite:///./test.db" if os.getenv("USE_SQLITE_FOR_TESTS") == "true" else "postgresql+psycopg://postgres:postgres@localhost:5432/projectpulse"
    )
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "projectpulse")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache

def get_settings() -> Settings:
    return Settings()


settings = get_settings()
