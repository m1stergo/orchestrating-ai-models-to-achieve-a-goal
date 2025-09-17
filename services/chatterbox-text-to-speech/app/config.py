from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Describe Image Service settings."""
    
    # API settings
    API_TITLE: str = "Chatterbox Text to Speech Service"
    API_DESCRIPTION: str = "AI service for text to speech conversion"
    API_VERSION: str = "/api/v1"
    PORT: int = 8000

    HUGGINGFACE_CACHE_DIR: Optional[str] = None
    
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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
