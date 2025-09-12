from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Describe Image Service settings."""
    
    # API settings
    API_TITLE: str = "Chatterbox Text to Speech Service"
    API_DESCRIPTION: str = "AI service for text to speech conversion"
    API_VERSION: str = "/api/v1"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
