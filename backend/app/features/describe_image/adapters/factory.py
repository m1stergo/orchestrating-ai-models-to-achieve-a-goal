"""
Factory for creating and managing image description adapters.
"""
import logging
from typing import Dict, Type, List

from .base import ImageDescriptionAdapter
from .openai_adapter import OpenAIAdapter
from .gemini_adapter import GeminiAdapter
from .qwen_adapter import QwenAdapter

logger = logging.getLogger(__name__)


class ImageDescriptionAdapterFactory:
    """Factory for creating and managing image description adapters (strategy pattern)."""
    
    # Available adapters mapped by name
    _adapters: Dict[str, Type[ImageDescriptionAdapter]] = {
        "openai": OpenAIAdapter,
        "gemini": GeminiAdapter,
        "qwen": QwenAdapter,
    }
    
    @classmethod
    def get_adapter(cls, model_name: str) -> ImageDescriptionAdapter:
        """
        Get an adapter instance by model name.
        
        Args:
            model_name: Name of the model to use (openai, gemini, qwen)
            
        Returns:
            An adapter instance
            
        Raises:
            ValueError: If the model is not supported
        """
        if model_name not in cls._adapters:
            available = list(cls._adapters.keys())
            raise ValueError(f"Model not supported: {model_name}. Available models: {available}")
        
        adapter_class = cls._adapters[model_name]
        return adapter_class()
    
    @classmethod
    def list_available_models(cls) -> List[str]:
        """
        Get a list of all available model names.
        
        Returns:
            List of available model names
        """
        return list(cls._adapters.keys())
