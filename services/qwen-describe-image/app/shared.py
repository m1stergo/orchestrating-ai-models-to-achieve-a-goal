"""
Shared module for global variables and instances.
This helps avoid circular imports between app modules.
"""
from .model import QwenModel

# Global model instance
model_instance = QwenModel()
model_loaded = False
