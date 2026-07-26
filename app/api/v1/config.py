"""
Configuration settings for the FastAPI application
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    API_PORT: int = 8080
    API_BASE_PATH: str = "api/v1"

    # YouTube API settings
    API_KEY: str | None = os.getenv("API_KEY")
    AUTH_FILE: str | None = os.getenv("AUTH_FILE")
    SCOPES: list[str] = os.getenv("SCOPES", "")

    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8080))

    # API settings
    MAX_RESULTS_DEFAULT: int = 50
    MAX_RESULTS_MAX: int = 50

    # Database settings
    DB_SYSTEM: str = os.getenv("DB_SYSTEM", "postgresql")
    DB_NAME: str = os.getenv("DB_NAME", "db")
    DB_USER: str = os.getenv("DB_USER", "user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 