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
    PORT: int = 8000

    # Model configurations
    MISTRAL_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.1"
    
    # HuggingFace cache directory
    HUGGINGFACE_TOKEN: Optional[str] = None

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
