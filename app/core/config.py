from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Pentulz Backend"
    environment: str = "dev"
    debug: bool = False

    class Config:
        env_file = ".env"
        env_prefix = "APP_"

@lru_cache
def get_settings() -> Settings:
    return Settings()
