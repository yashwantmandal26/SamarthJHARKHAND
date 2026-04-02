"""
Samarth Configuration Module
Loads environment variables and provides typed config access.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    """Application settings loaded from environment variables."""

    # LLM Provider: 'ollama' for local, 'gemini' for cloud
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")

    # Gemini (Cloud)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Ollama (Local)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3:8b")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./samarth.db")
    DB_PATH: Path = PROJECT_ROOT / "backend" / "samarth.db"

    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Server
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

    # App
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Paths
    SCHEMES_DATA_PATH: Path = Path(__file__).parent / "data" / "schemes.json"


settings = Settings()
