from typing import Dict, Type, Optional, List
from .base import BaseGenerateDescriptionModel
from .openai import OpenAIModel
from .gemini import GeminiModel
# from .mistral import MistralModel
import logging

logger = logging.getLogger(__name__)


class GenerateDescriptionModelFactory:
    """Factory class to create appropriate text generation model."""
    
    # Available models
    _models: Dict[str, Type[BaseGenerateDescriptionModel]] = {
        "openai": OpenAIModel,
        "gemini": GeminiModel,
        # "mistral": MistralModel,
    }
    
    @classmethod
    def get_model(cls, model_name: Optional[str] = None) -> BaseGenerateDescriptionModel:
        """
        Get the appropriate text generation model.
        
        Args:
            model_name: The preferred model name (e.g., "openai", "gemini")
        
        Returns:
            BaseGenerateDescriptionModel: The model instance
        
        Raises:
            ValueError: If no model is available or invalid
        """
        try:
            if model_name:
                if model_name not in cls._models:
                    available = list(cls._models.keys())
                    raise ValueError(f"Unknown model '{model_name}'. Available: {available}")
                
                model_class = cls._models[model_name]
                model = model_class()
                
                if model.is_available():
                    logger.info(f"Using requested model: {model_name}")
                    return model
                else:
                    logger.warning(f"Requested model '{model_name}' is not available, falling back to default")
            
            # If no model is available
            raise ValueError("No text generation model is available. Please check your configuration.")
            
        except Exception as e:
            logger.error(f"Error creating model: {str(e)}")
            raise
    
    @classmethod
    def list_keys(cls) -> List[str]:
        """Get list of all model names."""
        return list(cls._models.keys())
