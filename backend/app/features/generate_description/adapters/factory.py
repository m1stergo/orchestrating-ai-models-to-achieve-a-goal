"""
Factory for creating and managing text generation adapters.
"""
import logging
from typing import Dict, Type, List

from .base import GenerateDescriptionAdapter
from .openai_adapter import OpenAIAdapter
from .gemini_adapter import GeminiAdapter
from .mistral_adapter import MistralAdapter

logger = logging.getLogger(__name__)


class GenerateDescriptionAdapterFactory:
    """Factory for creating and managing text generation adapters (strategy pattern)."""
    
    # Available adapters mapped by name
    _adapters: Dict[str, Type[GenerateDescriptionAdapter]] = {
        "openai": OpenAIAdapter,
        "gemini": GeminiAdapter,
        "mistral": MistralAdapter,
    }
    
    @classmethod
    def get_adapter(cls, model_name: str) -> GenerateDescriptionAdapter:
        """
        Get a text generation adapter by model name.
        
        Args:
            model_name: Name of the model to use
            
        Returns:
            GenerateDescriptionAdapter: An adapter for the specified model
            
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
        List all available text generation models.
        
        Returns:
            List[str]: List of available model names
        """
        return list(cls._adapters.keys())
