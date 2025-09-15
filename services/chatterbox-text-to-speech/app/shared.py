"""
Shared module for global variables and instances.
This helps avoid circular imports between app modules.
"""
from .handler import ChatterboxHandler

# Global model instance
handler = ChatterboxHandler('chatterbox')
