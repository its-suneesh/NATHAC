from pydantic import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str

    # 🔐 JWT Secret
    JWT_SECRET_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
