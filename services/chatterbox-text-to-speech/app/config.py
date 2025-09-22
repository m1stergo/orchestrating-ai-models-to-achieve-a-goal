"""Configuration module for the Chatterbox Text-to-Speech service.

This module defines the configuration settings for the text-to-speech service
using Pydantic's BaseSettings for environment variable loading, validation,
and type conversion.

The configuration includes API metadata, model settings, MinIO storage settings,
and file paths for caching and temporary storage.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Settings for the Chatterbox Text-to-Speech service.
    
    This class defines all configuration parameters for the service,
    loading values from environment variables, .env file, or defaults.
    
    Attributes:
        API_TITLE: Title for the API documentation
        API_DESCRIPTION: Description for the API documentation
        API_VERSION: Version prefix for the API endpoints
        PORT: Port number for the service to listen on
        MINIO_*: Settings for MinIO storage connection and buckets
        HUGGINGFACE_CACHE_DIR: Directory for caching HuggingFace models
        TORCH_HOME: Directory for PyTorch models cache
        TMPDIR: Directory for temporary files
        MODELS_DIR: Directory for storing downloaded models
        CHATTERBOX_MODEL_NAME: HuggingFace model name for the TTS model
        PROMPT: Default prompt for promotional script generation
        PYTORCH_CUDA_ALLOC_CONF: PyTorch CUDA memory allocation configuration
    """
    
    # API settings for documentation and routing
    API_TITLE: str = "Chatterbox Text to Speech Service"  # Title in API documentation
    API_DESCRIPTION: str = "AI service for text to speech conversion"  # Service description
    API_VERSION: str = "/api/v1"  # API version prefix
    PORT: int = 8003  # Port to run the service on

    # MinIO storage settings for audio file storage
    MINIO_ENDPOINT_URL: str = None  # MinIO server endpoint URL
    MINIO_ACCESS_KEY: str = None  # Access key for MinIO authentication
    MINIO_SECRET_KEY: str = None  # Secret key for MinIO authentication
    MINIO_SECURE: bool = True  # Whether to use HTTPS for MinIO connections
    MINIO_REGION: Optional[str] = None  # MinIO region name (if applicable)
    
    # MinIO bucket configuration
    MINIO_PUBLIC_BUCKET: str = "public"  # Bucket for publicly accessible files
    MINIO_TEMP_BUCKET: str = "temp"  # Bucket for temporary files
    MINIO_PUBLIC_URL: str = None  # Public URL for accessing the MinIO bucket

    # Caching and storage paths (optimized for RunPod volume mounting)
    HUGGINGFACE_CACHE_DIR: Optional[str] = "/runpod-volume/huggingface"  # HuggingFace cache
    TORCH_HOME: Optional[str] = "/runpod-volume/torch"  # PyTorch models cache
    TMPDIR: Optional[str] = "/runpod-volume/tmp"  # Temporary directory
    MODELS_DIR: Optional[str] = "/runpod-volume/models"  # Model storage

    # TTS model configuration
    CHATTERBOX_MODEL_NAME: str = "ResembleAI/chatterbox"  # Official ChatterboxTTS model on HuggingFace

    # Default prompt template for promotional video scripts
    PROMPT: Optional[str] = """
    Create a short VOICEOVER TEXT for a Reels/TikTok promotional video about the product.

    Objective:
    - Clearly explain the product's purpose and function.
    - Describe its main characteristics: color, material, and shape.

    Rules:
    - Provide ONLY the narration lines, no scene directions or stage descriptions.
    - Start with a strong hook that grabs attention.
    - Keep the style natural, conversational, and energetic, with short, punchy sentences.
    - Structure: Hook → Purpose & Function → Characteristics (color, material, shape) → Call-to-action.
    - Length suitable for a video under 30 seconds.
    - Avoid emojis and marketing fluff. Keep it direct and simple.
    """

    # PyTorch CUDA memory optimization settings
    PYTORCH_CUDA_ALLOC_CONF: Optional[str] = "max_split_size_mb:128,garbage_collection_threshold:0.8"
    

    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"  # Path to .env file for environment variables
        case_sensitive = True  # Environment variable names are case-sensitive


# Create a singleton settings instance
settings = Settings()
