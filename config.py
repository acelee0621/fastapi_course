from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # static files
    STATIC_DIR: str
    STATIC_URL: str
    STATIC_NAME: str
    # debug mode
    DEBUG_MODE: bool
    # SMTP
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str    
    
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        # env_prefix = "FASTAPI_"
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


config = Settings()
