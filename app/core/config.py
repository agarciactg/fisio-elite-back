from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Fisio Élite API"
    SECRET_KEY: str
    DATABASE_URL: PostgresDsn

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
