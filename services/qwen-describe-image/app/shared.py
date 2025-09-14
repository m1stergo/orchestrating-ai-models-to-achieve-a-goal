"""
Shared module for global variables and instances.
This helps avoid circular imports between app modules.
"""
from .handler import QwenHandler
from .config import settings

# Global model instance
handler = QwenHandler(settings.QWEN_MODEL_NAME)
