from pydantic_settings import BaseSettings
from typing import Optional
import tomllib
from pathlib import Path


def get_version() -> str:
    """Read version from pyproject.toml"""
    try:
        pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        return pyproject_data["project"]["version"]
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return "1.0.0"  # fallback version


class Settings(BaseSettings):
    """Describe Image Service settings."""
    
    # API settings
    API_TITLE: str = "Chatterbox Text to Speech Service"
    API_DESCRIPTION: str = "AI service for text to speech conversion"
    API_VERSION: str = get_version()
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
