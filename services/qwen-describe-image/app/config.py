from pydantic_settings import BaseSettings
from typing import Optional
import tomllib
from pathlib import Path


def get_version() -> str:
    """Read version from pyproject.toml"""
    try:
        # qwen-describe-image/src/config.py -> up to service root
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
    
    
    # Model Configuration
    QWEN_MODEL_NAME: str = "Qwen/Qwen2.5-VL-7B-Instruct"
    QWEN_MAX_MEMORY_GPU: str = "14GB"
    QWEN_MAX_MEMORY_CPU: str = "8GB"
    
    # HuggingFace cache directory
    HUGGINGFACE_CACHE_DIR: Optional[str] = None
    
    # Custom prompt template
    PROMPT: Optional[str] = """
    Analyze the main product in the image provided. Focus exclusively on the product itself. Based on your visual analysis of the product, complete the following template. If any field cannot be determined from the image, state "Not visible" or "Unknown".
    Image description: A brief but comprehensive visual description of the item, detailing its color, shape, material, and texture.
    Product type: What is the object?
    Material: What is it made of? Be specific if possible (e.g., "leather," "plastic," "wood").
    Keywords: List relevant keywords that describe the item's appearance or function.
    """
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
