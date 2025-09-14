"""
Factory for creating and managing text generation adapters.
"""
import logging
from typing import Dict, Type

from app.shared.adapter import Adapter
from app.shared.schemas import ServiceResponse
from .openai_adapter import OpenAIAdapter
from .gemini_adapter import GeminiAdapter
from .mistral_adapter import MistralAdapter

logger = logging.getLogger(__name__)


class GenerateDescriptionAdapterFactory:
    """Factory for creating and managing text generation adapters (strategy pattern)."""
    
    # Available adapters mapped by name
    _adapters: Dict[str, Type[Adapter]] = {
        "openai": OpenAIAdapter,
        "gemini": GeminiAdapter,
        "mistral": MistralAdapter,
    }
    
    @classmethod
    def get_adapter(cls, model_name: str) -> Adapter:
        """
        Get a text generation adapter by model name.
        
        Args:
            model_name: Name of the model to use
            
        Returns:
            Adapter: An adapter for the specified model
            
        Raises:
            ValueError: If the model is not supported
        """
        if model_name not in cls._adapters:
            available = list(cls._adapters.keys())
            raise ValueError(f"Model not supported: {model_name}. Available models: {available}")
        
        adapter_class = cls._adapters[model_name]
        return adapter_class()
    
    @classmethod
    def list_available_models(cls) -> ServiceResponse:
        """
        Get a list of all available model names.
        
        Returns:
            ServiceResponse: Service response with list of available model names
        """
        return ServiceResponse(
            status="IDLE",
            message="Available models retrieved successfully",
            data=list(cls._adapters.keys())
        )
