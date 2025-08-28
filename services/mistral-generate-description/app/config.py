from pydantic_settings import BaseSettings
from typing import Optional
import tomllib
from pathlib import Path


def get_version() -> str:
    """Read version from pyproject.toml"""
    try:
        pyproject_path = Path(__file__).parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        return pyproject_data["project"]["version"]
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return "1.0.0"  # fallback version


class Settings(BaseSettings):
    """Generate Description Service settings."""
    
    # API settings
    API_TITLE: str = "Generate Description Service"
    API_DESCRIPTION: str = "AI service for text generation and description"
    API_VERSION: str = get_version()
    
    # External API Keys
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    HUGGINGFACE_TOKEN: Optional[str] = None
    
    # Model configurations
    OPENAI_MODEL: str = "gpt-4o"
    GEMINI_MODEL: str = "gemini-1.5-flash"
    MISTRAL_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
