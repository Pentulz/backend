from functools import lru_cache

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

    name: str = "Pentulz Backend"
    environment: str = "dev"
    debug: bool = False

    # API
    API_PREFIX: str = "/api/v1"

    # CORS
    CORS_ALLOW_ORIGINS: list[str] = []

    # DATABASE
    DATABASE_HOST: str = "database"  # Same as service name
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_NAME: str = "pentulz"

    def get_database_url(self) -> str:
        """URL for the database connection."""
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
