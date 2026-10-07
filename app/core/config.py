from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 1
    USERNAME: str
    PASSWORD: str 
    
    COMPOSE_PROJECT_NAME: str

    # Where it listens, and what docker-compose publishes - one line in .env
    # moves both. Declared because pydantic rejects any .env key it does not
    # know: PORT=... in .env alone would stop the service at startup.
    HOST: str = "0.0.0.0"
    PORT: int = 5014

    
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo"

    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"


    class Config:
        env_file = ".env"

settings = Settings()