"""
Factory for creating and managing image description adapters.
"""
import logging
from typing import Dict, Type

from .openai_adapter import OpenAIAdapter
from .gemini_adapter import GeminiAdapter
from .qwen_adapter import QwenAdapter
from app.shared.adapter import Adapter
from app.shared.schemas import ServiceResponse

logger = logging.getLogger(__name__)


class ImageDescriptionAdapterFactory:
    """Factory for creating and managing image description adapters (strategy pattern)."""
    
    # Available adapters mapped by name
    _adapters: Dict[str, Type[Adapter]] = {
        "openai": OpenAIAdapter,
        "gemini": GeminiAdapter,
        "qwen": QwenAdapter,
    }
    
    @classmethod
    def get_adapter(cls, model_name: str) -> Adapter:
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
