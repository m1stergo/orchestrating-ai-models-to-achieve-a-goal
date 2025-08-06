from typing import Dict, Type, Optional, List
from .base import ImageDescriptionModel
from .qwen import QwenModel
from .openai import OpenAIVisionModel
from .gemini import GeminiModel
import logging

logger = logging.getLogger(__name__)


class ImageDescriptionModelFactory:
    """Factory class to create appropriate image description model."""
    
    # Available models
    _models: Dict[str, Type[ImageDescriptionModel]] = {
        "qwen": QwenModel,
        "openai": OpenAIVisionModel,
        "gemini": GeminiModel,
    }
    
    @classmethod
    def get_model(cls, model_name: Optional[str] = None) -> ImageDescriptionModel:
        """
        Get the appropriate image description model.
        
        Args:
            model_name: The preferred model name (e.g., "qwen", "openai")
        
        Returns:
            ImageDescriptionModel: The model instance
        
        Raises:
            ValueError: If no model is available or preferred model is invalid
        """
        try:
            # If a specific model is requested
            if model_name:
                if model_name not in cls._models:
                    available = list(cls._models.keys())
                    raise ValueError(f"Unknown model '{model_name}'. Available: {available}")
                
                model_class = cls._models[model_name]
                model = model_class()
                
                if model.is_available():
                    logger.info(f"Using requested model: {model_name}")
                    logger.info(f"Mode ES _______________: {model}")
                    return model
                else:
                    logger.warning(f"Requested model '{model_name}' is not available, falling back to default")
            logger.info("LLEGA HASTA EL ERROR")
            # If no model is available
            raise ValueError("No image description model is available. Please check your configuration.")
            
        except Exception as e:
            logger.error(f"Error creating model: {str(e)}")
            raise
    
    @classmethod
    def list_keys(cls) -> List[str]:
        """Get list of all model names."""
        return list(cls._models.keys())
        """Get information about all available models."""
        models_info = {}
        
        for name, model_class in cls._models.items():
            try:
                model = model_class()
                is_available = model.is_available()
                
                # Get model info based on the model type
                if name == "openai":
                    info = {
                        "type": "api",
                        "provider": "OpenAI",
                        "description": "GPT-4 Vision for image description",
                        "available": is_available,
                        "requires_api_key": True
                    }
                elif name == "gemini":
                    info = {
                        "type": "api",
                        "provider": "Google",
                        "description": "Gemini Vision for image description",
                        "available": is_available,
                        "requires_api_key": True
                    }
                elif name == "qwen":
                    info = {
                        "type": "local",
                        "provider": "Qwen",
                        "description": "Qwen-VL for local image description",
                        "available": is_available,
                        "requires_api_key": False
                    }
                else:
                    info = {
                        "type": "unknown",
                        "provider": "Unknown",
                        "description": f"{name} model",
                        "available": is_available,
                        "requires_api_key": False
                    }
                
                models_info[name] = info
                
            except Exception as e:
                logger.warning(f"Error checking availability for {name}: {str(e)}")
                models_info[name] = {
                    "type": "unknown",
                    "provider": "Unknown",
                    "description": f"{name} model (error checking availability)",
                    "available": False,
                    "requires_api_key": False
                }
        
        return models_info