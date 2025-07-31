from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    # API settings
    API_V1_STR: str = "/api/v1"
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
    
    # Microservice URLs
    DESCRIBE_IMAGE_SERVICE_URL: str = "http://localhost:8001"
    GENERATE_DESCRIPTION_SERVICE_URL: str = "http://localhost:8002"
    
    # Computed property for image URL construction
    @property
    def images_url(self) -> str:
        """Get the full URL path for images."""
        return f"{self.STATIC_URL}/images"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
