import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Прибираємо os.getenv! Pydantic сам підтягне значення з файлу
    SECRET_KEY: str
    ALGORITHM: str
    SQLALCHEMY_DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_TIME: int

    model_config = SettingsConfigDict(
        # Важливо: переконайтеся, що шлях правильний.
        # BASE_DIR вказує на папку Shop, тому .env шукаємо там.
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()