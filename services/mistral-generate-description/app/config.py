"""Configuration module for the Mistral Generate Description service.

This module defines the configuration settings for the text generation service
using Pydantic's BaseSettings for environment variable loading, validation,
and type conversion.

The configuration includes API metadata, model settings, and file paths for
caching and temporary storage, as well as default prompts for generation.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Settings for the Mistral Generate Description service.
    
    This class defines all configuration parameters for the service,
    loading values from environment variables, .env file, or defaults.
    
    Attributes:
        API_TITLE: Title for the API documentation
        API_DESCRIPTION: Description for the API documentation
        API_VERSION: Version prefix for the API endpoints
        PORT: Port number for the service to listen on
        MISTRAL_MODEL_NAME: HuggingFace model name/path for the Mistral model
        HF_TOKEN: HuggingFace API token for accessing gated models
        HUGGINGFACE_CACHE_DIR: Directory for caching HuggingFace models
        TORCH_HOME: Directory for PyTorch models cache
        TMPDIR: Directory for temporary files
        MODELS_DIR: Directory for storing downloaded models
        PROMPT: Default prompt template for product description generation
        PYTORCH_CUDA_ALLOC_CONF: PyTorch CUDA memory allocation configuration
    """
    
    # API settings for documentation and routing
    API_TITLE: str = "Generate Description Service"  # Title in API documentation
    API_DESCRIPTION: str = "AI service for text generation and description"  # Service description
    API_VERSION: str = "/api/v1"  # API version prefix
    PORT: int = 8000  # Port to run the service on

    # Model configuration for Mistral LLM
    MISTRAL_MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.1"  # HuggingFace model ID
    #MISTRAL_MODEL_NAME: str = "teknium/OpenHermes-2.5-Mistral-7B"  # Alternative model
    
    # HuggingFace authentication
    HF_TOKEN: Optional[str] = None  # Token for accessing gated models

    # Caching and storage paths (optimized for RunPod volume mounting)
    HUGGINGFACE_CACHE_DIR: Optional[str] = "/runpod-volume/huggingface"  # HuggingFace cache
    TORCH_HOME: Optional[str] = "/runpod-volume/torch"  # PyTorch models cache
    TMPDIR: Optional[str] = "/runpod-volume/tmp"  # Temporary directory
    MODELS_DIR: Optional[str] = "/runpod-volume/models"  # Model storage

    # Default prompt template for product descriptions
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

    # PyTorch CUDA memory optimization settings
    PYTORCH_CUDA_ALLOC_CONF: Optional[str] = "max_split_size_mb:128,garbage_collection_threshold:0.8"
    
    
    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"  # Path to .env file for environment variables
        case_sensitive = True  # Environment variable names are case-sensitive


# Create a singleton settings instance
settings = Settings()
