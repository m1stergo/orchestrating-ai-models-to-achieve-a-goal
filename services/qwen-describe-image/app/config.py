"""Configuration module for the AI service.

This module defines the configuration settings for the image description service
using Pydantic's BaseSettings for environment variable loading, validation,
and type conversion.

The configuration includes API metadata, model settings, and file paths for
caching and temporary storage.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Settings for the Qwen Describe Image service.
    
    This class defines all configuration parameters for the service,
    loading values from environment variables, .env file, or defaults.
    
    Attributes:
        API_TITLE: Title for the API documentation
        API_DESCRIPTION: Description for the API documentation
        API_VERSION: Version prefix for the API endpoints
        PORT: Port number for the service to listen on
        QWEN_MODEL_NAME: HuggingFace model name/path for the Qwen model
        QWEN_MAX_MEMORY_GPU: Maximum GPU memory allocation for the model
        QWEN_MAX_MEMORY_CPU: Maximum CPU memory allocation for the model
        HUGGINGFACE_CACHE_DIR: Directory for caching HuggingFace models
        TORCH_HOME: Directory for PyTorch models cache
        TMPDIR: Directory for temporary files
        MODELS_DIR: Directory for storing downloaded models
        PROMPT: Default prompt for image description
        PYTORCH_CUDA_ALLOC_CONF: PyTorch CUDA memory allocation configuration
    """
    # API settings for documentation and routing
    API_TITLE: str = "Describe Image Service"  # Title in API documentation
    API_DESCRIPTION: str = "AI service for image description and analysis"  # Service description
    API_VERSION: str = "/api/v1"  # API version prefix
    PORT: int = 8001  # Port to run the service on

    # Model configuration for Qwen VL model
    QWEN_MODEL_NAME: str = "Qwen/Qwen2.5-VL-7B-Instruct"  # HuggingFace model ID
    QWEN_MAX_MEMORY_GPU: str = "22GiB"  # Maximum GPU memory to use
    QWEN_MAX_MEMORY_CPU: str = "3GiB"  # Maximum CPU memory to use

    # Caching and storage paths (optimized for RunPod volume mounting)
    HUGGINGFACE_CACHE_DIR: Optional[str] = "/runpod-volume/huggingface"  # HuggingFace cache
    TORCH_HOME: Optional[str] = "/runpod-volume/torch"  # PyTorch models cache
    TMPDIR: Optional[str] = "/runpod-volume/tmp"  # Temporary directory
    MODELS_DIR: Optional[str] = "/runpod-volume/models"  # Model storage

    # Model parameters
    PROMPT: Optional[str] = "Describe this image in detail"  # Default prompt for image description

    # PyTorch CUDA memory optimization settings
    PYTORCH_CUDA_ALLOC_CONF: Optional[str] = "max_split_size_mb:128,garbage_collection_threshold:0.8"
    
    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"  # Path to .env file for environment variables
        case_sensitive = True  # Environment variable names are case-sensitive


# Create a singleton settings instance
settings = Settings()
