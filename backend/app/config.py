from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Orchestration API"
    
    # Database settings
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "postgres")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "orchestration_db")
    DATABASE_URL: Optional[str] = os.getenv(
        "DATABASE_URL",
        f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    )
    
    # Backend URL settings
    BASE_URL: str = "http://localhost:8000"
    
    # Image storage settings
    IMAGES_DIR: Path = Path("app/static/images")
    STATIC_URL: str = "http://localhost:8000/static"
    
    # Computed property for image URL construction
    @property
    def images_url(self) -> str:
        """Get the full URL path for images."""
        return f"{self.STATIC_URL}/images"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
