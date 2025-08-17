"""
Factory for creating and managing text-to-speech adapters.
"""
import logging
from typing import Dict, Type, List

from .base import TextToSpeechAdapter
from .chatterbox_adapter import ChatterboxAdapter

logger = logging.getLogger(__name__)


class TextToSpeechAdapterFactory:
    """Factory for creating and managing text-to-speech adapters (strategy pattern)."""
    
    # Available adapters mapped by name
    _adapters: Dict[str, Type[TextToSpeechAdapter]] = {
        "chatterbox": ChatterboxAdapter,
    }
    
    @classmethod
    def get_adapter(cls, model_name: str = None) -> TextToSpeechAdapter:
        """
        Get a text-to-speech adapter by model name.
        
        Args:
            model_name: Name of the model to use (defaults to 'chatterbox')
            
        Returns:
            TextToSpeechAdapter: An adapter for the specified model
            
        Raises:
            ValueError: If the model is not supported
        """
        # Default to chatterbox if no model specified
        if model_name is None:
            model_name = "chatterbox"
            
        if model_name not in cls._adapters:
            available = list(cls._adapters.keys())
            raise ValueError(f"Modelo TTS no soportado: {model_name}. Disponibles: {available}")
        
        adapter_class = cls._adapters[model_name]
        return adapter_class()
    
    @classmethod
    def list_available_models(cls) -> List[str]:
        """
        List all available text-to-speech models.
        
        Returns:
            List[str]: List of available model names
        """
        return list(cls._adapters.keys())
