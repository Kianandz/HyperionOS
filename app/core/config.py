import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = os.getenv("TITLE", "HyperionOS")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "hyperion-secret-key-change-this")
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()