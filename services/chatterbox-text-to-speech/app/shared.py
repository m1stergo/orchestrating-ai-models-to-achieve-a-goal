"""
Shared module for global variables and instances.
This helps avoid circular imports between app modules.
"""
from .model import ChatterboxModel

# Global model instance
model_instance = ChatterboxModel()
model_loaded = False
