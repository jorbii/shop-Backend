import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    SECRET_KEY: str=os.getenv('SECRET_KEY')
    ALGORITHM: str=os.getenv("ALGORITHM")
    SQLALCHEMY_DATABASE_URL: str=os.getenv("SQLALCHEMY_DATABASE_URL")
    ACCESS_TOKEN_EXPIRE_MINUTES: int=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_TIME: int=os.getenv("REFRESH_TOKEN_EXPIRE_TIME")

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()