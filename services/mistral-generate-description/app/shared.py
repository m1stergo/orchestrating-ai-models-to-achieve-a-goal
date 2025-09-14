"""
Shared module for global variables and instances.
This helps avoid circular imports between app modules.
"""
from .handler import MistralHandler
from .config import settings

# Global model instance
handler = MistralHandler(settings.MISTRAL_MODEL_NAME)
