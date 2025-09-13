from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Generate Description Service settings."""
    
    # API settings
    API_TITLE: str = "Generate Description Service"
    API_DESCRIPTION: str = "AI service for text generation and description"
    API_VERSION: str = "/api/v1"
    PORT: int = 8000

    # Model configurations
    MISTRAL_MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.1"
    
    # HuggingFace cache directory
    HF_TOKEN: Optional[str] = None
    HUGGINGFACE_CACHE_DIR: Optional[str] = None


    # Custom prompt template
    PROMPT: Optional[str] = """
    You are a professional e-commerce copywriter.
    Write a short, concise product description for ecommerce page.

    Rules:
    - Title must be concise, clear, and descriptive (max 10 words)
    - Description must be direct, simple, and factual (40-60 words max)
    - Use short sentences, avoid marketing fluff and adjectives like "elevate", "charming", "whimsy"
    - Focus on features first, then benefits
    - Keywords must not repeat, must be relevant for SEO
    """
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
