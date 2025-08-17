"""
Shared module for global variables and instances.
This helps avoid circular imports between app modules.
"""
from .model import MistralModel

# Global model instance
model_instance = MistralModel()
model_loaded = False
