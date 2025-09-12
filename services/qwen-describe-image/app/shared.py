"""
Shared module for global variables and instances.
This helps avoid circular imports between app modules.
"""
from .model import QwenModel
from .common import InferenceHandler
from .config import settings

# Global model instance
model_instance = QwenModel()

handler = InferenceHandler(
    model=model_instance,
    model_name=settings.QWEN_MODEL_NAME,
)
