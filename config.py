from functools import lru_cache
from pydantic_settings import BaseSettings





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
    
    class Config:
        env_file = (".env", ".env.local")  # 后面的文件会覆盖前面的文件
        #env_prefix = "FASTAPI_"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
    
config = Settings()