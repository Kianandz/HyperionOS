import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str = os.getenv("TITLE")

    VERSION: str = os.getenv("VERSION")

    PORT: str = os.getenv("PORT")

    SECRET_KEY: str = os.getenv("SECRET_KEY")

    DEBUG: bool = True

    session_max_age: int = os.getenv("SESSION_MAX_AGE")

    session_secure: bool = os.getenv("SESSION_SECURE")

    class Config:

        env_file = ".env"


settings = Settings()
