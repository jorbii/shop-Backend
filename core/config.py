# import os
# from pydantic_settings import BaseSettings, SettingsConfigDict
#
# class Settings(BaseSettings):
#     SECRET_KEY: str
#     SECURITY_KEY: str
#     ALGORITHM: str
#     ACCESS_TOKEN_EXPIRE_MINUTES: int
#
#     model_config = SettingsConfigDict(
#         # Шукаємо .env у тій самій папці, де лежить скрипт, або в корені
#         env_file=os.path.join(os.path.dirname(__file__), ".env"),
#         env_file_encoding='utf-8',
#         extra='ignore' # Не падати, якщо є зайві змінні
#     )
#
# settings = Settings()