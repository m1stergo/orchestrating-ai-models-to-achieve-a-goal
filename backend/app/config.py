"""Application configuration module.

This module defines the Settings class that represents the application configuration.
It uses Pydantic's BaseSettings to provide type validation and automatic loading
of environment variables.
"""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings and configuration.
    
    This class represents all configuration options for the application.
    Values are loaded from environment variables, .env file, or defaults.
    
    Attributes:
        API_VERSION: Version prefix for all API endpoints.
        PROJECT_NAME: Name of the project displayed in API documentation.
        DATABASE_HOST: Host address of the database server.
        DATABASE_PORT: Port of the database server.
        DATABASE_USER: Username for database authentication.
        DATABASE_PASSWORD: Password for database authentication.
        DATABASE_NAME: Name of the database.
        DATABASE_URL: Complete database URL for SQLAlchemy.
        PORT: Port on which the server will run.
        BASE_URL: Base URL of the server.
        IMAGES_DIR: Directory where uploaded images are stored.
        STATIC_URL: URL for accessing static files.
        VOICE_MODELS_CONFIG: Path to voice models configuration file.
        AUDIO_DIR: Directory where audio files are stored.
        AUDIO_URL: URL for accessing audio files.
        EXPORTS_DIR: Directory where export files are stored.
    """
    
    # API settings
    API_VERSION: str = "/api/v1"  # Version prefix for all API endpoints
    PROJECT_NAME: str = "AI Orchestration API"  # Project name for API documentation
    
    # Database settings
    DATABASE_HOST: str = "localhost"  # Database server hostname
    DATABASE_PORT: str = "5432"  # Database server port
    DATABASE_USER: str = "postgres"  # Database username
    DATABASE_PASSWORD: str = "postgres"  # Database password
    DATABASE_NAME: str = "orchestration_db"  # Database name
    DATABASE_URL: Optional[str] = None  # Full database connection string (built from components if not provided)
    
    def __init__(self, **kwargs):
        """Initialize settings with values from environment and defaults.
        
        Args:
            **kwargs: Override any setting values via keyword arguments.
        """
        super().__init__(**kwargs)
        # Build DATABASE_URL if not provided
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    # Backend URL settings
    PORT: int = 8000  # Port on which the API server will run
    BASE_URL: str = "http://localhost:8000"  # Base URL for the API server
    
    # Image storage settings
    IMAGES_DIR: Path = Path("app/static/images")  # Directory for storing uploaded images
    STATIC_URL: str = "http://localhost:8000/static"  # Base URL for static files
    
    # Voice models configuration
    VOICE_MODELS_CONFIG: Path = Path("app/features/text_to_speech/voice_models.json")  # Path to voice models config file
    
    # Audio storage settings
    AUDIO_DIR: Path = Path("app/static/audio")  # Directory for storing audio files
    AUDIO_URL: str = "http://localhost:8000/static"  # Base URL for audio files
    
    # Export storage settings
    EXPORTS_DIR: Path = Path("app/static/exports")  # Directory for storing export files

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
        """Get the full URL path for accessing images.
        
        Returns:
            str: Complete URL path to the images directory
        """
        return f"{self.STATIC_URL}/images"
    
    # Computed property for audio URL construction
    @property
    def audio_url(self) -> str:
        """Get the full URL path for accessing audio files.
        
        Returns:
            str: Complete URL path to the audio directory
        """
        return f"{self.AUDIO_URL}/audio"
    
    class Config:
        """Configuration for Pydantic settings behavior."""
        env_file = ".env"  # Load environment variables from .env file
        case_sensitive = True  # Environment variables are case-sensitive


settings = Settings()
