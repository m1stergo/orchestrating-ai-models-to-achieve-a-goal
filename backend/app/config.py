from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    # API settings
    API_VERSION: str = "/api/v1"
    PROJECT_NAME: str = "AI Orchestration API"
    
    # Database settings
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: str = "5432"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_NAME: str = "orchestration_db"
    DATABASE_URL: Optional[str] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Build DATABASE_URL if not provided
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    # Backend URL settings
    BASE_URL: str = "http://localhost:8000"
    
    # Image storage settings
    IMAGES_DIR: Path = Path("app/static/images")
    STATIC_URL: str = "http://localhost:8000/static"
    
    # Voice models configuration
    VOICE_MODELS_CONFIG: Path = Path("app/config/voice_models.json")
    
    # Audio storage settings
    AUDIO_DIR: Path = Path("app/static/audio")
    AUDIO_URL: str = "http://localhost:8000/static"
    
    # Export storage settings
    EXPORTS_DIR: Path = Path("app/static/exports")
    
    # Microservice base URLs with API prefix
    DESCRIBE_IMAGE_QWEN_URL: str = "http://localhost:8001/api/v1"
    GENERATE_DESCRIPTION_MISTRAL_URL: str = "http://localhost:8002/api/v1"
    TTS_CHATTERBOX_URL: str = "http://localhost:8003/api/v1"
    
    # API Keys for external services
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    EXTERNAL_API_TOKEN: Optional[str] = None
    OPENAI_VISION_MODEL: Optional[str] = None
    GEMINI_VISION_MODEL: Optional[str] = None
    QWEN_VISION_MODEL: Optional[str] = None
    OPENAI_TEXT_MODEL: Optional[str] = None
    GEMINI_TEXT_MODEL: Optional[str] = None
    MISTRAL_TEXT_MODEL: Optional[str] = None

    # Computed property for image URL construction
    @property
    def images_url(self) -> str:
        """Get the full URL path for images."""
        return f"{self.STATIC_URL}/images"
    
    # Computed property for audio URL construction
    @property
    def audio_url(self) -> str:
        """Get the full URL path for audio files."""
        return f"{self.AUDIO_URL}/audio"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
