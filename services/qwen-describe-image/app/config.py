from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    API_TITLE: str = "Describe Image Service"
    API_DESCRIPTION: str = "AI service for image description and analysis"
    API_VERSION: str = "/api/v1"
    PORT: int = 8001

    # Model Configuration
    QWEN_MODEL_NAME: str = "Qwen/Qwen2.5-VL-7B-Instruct"
    QWEN_MAX_MEMORY_GPU: str = "22GiB"
    QWEN_MAX_MEMORY_CPU: str = "3GiB"

    # Caching / Temp (defaults target the network volume)
    HUGGINGFACE_CACHE_DIR: Optional[str] = "/runpod-volume/huggingface"
    TORCH_HOME: Optional[str] = "/runpod-volume/torch"
    TMPDIR: Optional[str] = "/runpod-volume/tmp"
    MODELS_DIR: Optional[str] = "/runpod-volume/models"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
