from pydantic_settings import BaseSettings
import tomllib
from pathlib import Path


def get_version() -> str:
    """Read version from pyproject.toml"""
    try:
        # qwen-describe-image/app/core/config.py -> up to service root
        pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        return pyproject_data["project"]["version"]
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return "1.0.0"  # fallback version


class Settings(BaseSettings):
    """Describe Image Service settings."""
    
    # API settings
    API_TITLE: str = "Describe Image Service"
    API_DESCRIPTION: str = "AI service for image description and analysis"
    API_VERSION: str = get_version()
    PORT: int = 8000
    
    QWEN_MODEL_NAME: str = "Qwen/Qwen2-VL-2B-Instruct"
    QWEN_MAX_MEMORY_GPU: str = "14GB"
    QWEN_MAX_MEMORY_CPU: str = "8GB"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
