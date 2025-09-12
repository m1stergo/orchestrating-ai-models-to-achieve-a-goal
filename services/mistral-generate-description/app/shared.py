"""
Shared module for global variables and instances.
This helps avoid circular imports between app modules.
"""
from .model import MistralModel
from .common import InferenceHandler
from .config import settings

# Global model instance
model_instance = MistralModel()

handler = InferenceHandler(
    model=model_instance,
    model_name=settings.MISTRAL_MODEL_NAME,
)
