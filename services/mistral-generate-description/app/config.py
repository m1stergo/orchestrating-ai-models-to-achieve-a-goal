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
    #MISTRAL_MODEL_NAME: str = "teknium/OpenHermes-2.5-Mistral-7B"
    
    # HuggingFace cache directory
    HF_TOKEN: Optional[str] = None

    # Caching / Temp (defaults target the network volume)
    HUGGINGFACE_CACHE_DIR: Optional[str] = "/runpod-volume/huggingface"
    TORCH_HOME: Optional[str] = "/runpod-volume/torch"
    TMPDIR: Optional[str] = "/runpod-volume/tmp"
    MODELS_DIR: Optional[str] = "/runpod-volume/models"

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

    PYTORCH_CUDA_ALLOC_CONF: Optional[str] = "max_split_size_mb:128,garbage_collection_threshold:0.8"
    
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
