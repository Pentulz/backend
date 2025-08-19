from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_prefix="APP_", 
        extra="ignore"       
    )

    app_name: str = "Pentulz Backend"
    environment: str = "dev"
    debug: bool = False

@lru_cache
def get_settings() -> Settings:
    return Settings()
