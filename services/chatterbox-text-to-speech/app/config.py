from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Describe Image Service settings."""
    
    # API settings
    API_TITLE: str = "Chatterbox Text to Speech Service"
    API_DESCRIPTION: str = "AI service for text to speech conversion"
    API_VERSION: str = "/api/v1"
    PORT: int = 8003

    # Minio storage settings
    MINIO_ENDPOINT_URL: str = None
    MINIO_ACCESS_KEY: str = None
    MINIO_SECRET_KEY: str = None
    MINIO_SECURE: bool = True
    MINIO_REGION: Optional[str] = None
    
    # Buckets configuration (new approach with separate buckets)
    MINIO_PUBLIC_BUCKET: str = "public"
    MINIO_TEMP_BUCKET: str = "temp"
    MINIO_PUBLIC_URL: str = None

    # Caching / Temp (defaults target the network volume)
    HUGGINGFACE_CACHE_DIR: Optional[str] = "/runpod-volume/huggingface"
    TORCH_HOME: Optional[str] = "/runpod-volume/torch"
    TMPDIR: Optional[str] = "/runpod-volume/tmp"
    MODELS_DIR: Optional[str] = "/runpod-volume/models"

    
    # Custom prompt template
    PROMPT: Optional[str] = """
    Create a short VOICEOVER TEXT for a Reels/TikTok promotional video about the product.

    Objective:
    - Clearly explain the product’s purpose and function.
    - Describe its main characteristics: color, material, and shape.

    Rules:
    - Provide ONLY the narration lines, no scene directions or stage descriptions.
    - Start with a strong hook that grabs attention.
    - Keep the style natural, conversational, and energetic, with short, punchy sentences.
    - Structure: Hook → Purpose & Function → Characteristics (color, material, shape) → Call-to-action.
    - Length suitable for a video under 30 seconds.
    - Avoid emojis and marketing fluff. Keep it direct and simple.
    """

    PYTORCH_CUDA_ALLOC_CONF: Optional[str] = "max_split_size_mb:128,garbage_collection_threshold:0.8"
    

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
