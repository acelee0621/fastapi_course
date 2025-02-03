from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    # static files
    STATIC_DIR: str
    STATIC_URL: str
    STATIC_NAME: str
    # debug mode
    DEBUG_MODE: bool
    
    class Config:
        env_file = (".env", ".env.local")  # 后面的文件会覆盖前面的文件
        #env_prefix = "FASTAPI_"
    
    
config = Settings()