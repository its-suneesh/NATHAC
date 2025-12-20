# app/core/config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensure we find the .env file in the root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOTENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    NATHAC_ENV: str = "dev"
    GEMINI_API_KEY: str
    
    model_config = SettingsConfigDict(
        env_file=str(DOTENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()