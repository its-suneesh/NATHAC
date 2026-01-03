from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 1
    USERNAME: str = "admin"
    PASSWORD: str = "password"

    
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo"

    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"


    class Config:
        env_file = ".env"

settings = Settings()