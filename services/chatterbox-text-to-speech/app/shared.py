"""
Shared module for global variables and instances.
This helps avoid circular imports between app modules.
"""
from .model import ChatterboxModel
from .common import InferenceHandler

# Global model instance
model_instance = ChatterboxModel()

handler = InferenceHandler(
    model=model_instance,
    model_name="chatterbox",
)
