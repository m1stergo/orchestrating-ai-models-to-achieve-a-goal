"""
Shared module for global variables and instances.
This helps avoid circular imports between app modules.
"""
from .handler import ChatterboxHandler
from .config import settings

# Global model instance - inicialización simple
handler = ChatterboxHandler(settings.CHATTERBOX_MODEL_NAME)
