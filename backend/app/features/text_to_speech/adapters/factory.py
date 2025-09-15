"""
Factory for creating and managing text_to_speech adapters.
"""
import logging
from typing import Dict, Type, List

from app.config import settings
from app.shared.adapter import Adapter
from .chatterbox_adapter import ChatterboxAdapter
from app.shared.schemas import ServiceResponse
from app.features.text_to_speech.schemas import VoiceModel
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class TextToSpeechAdapterFactory:
    """Factory for creating and managing text_to_speech adapters (strategy pattern)."""
    
    # Available adapters mapped by name
    _adapters: Dict[str, Type[Adapter]] = {
        "chatterbox": ChatterboxAdapter,
    }
    
    @classmethod
    def get_adapter(cls, model_name: str = None) -> Adapter:
        """
        Get a text_to_speech adapter by model name.
        
        Args:
            model_name: Name of the model to use (defaults to 'chatterbox')
            
        Returns:
            Adapter: An adapter for the specified model
            
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
    def list_available_voices(cls) -> ServiceResponse[List[VoiceModel]]:
        """
        List all available text_to_speech voices.
        
        Returns:
            List[VoiceModel]: List of available voices
        """
        voices: List[VoiceModel] = []
        try:
            config_file: Path = settings.VOICE_MODELS_CONFIG
            if not config_file.exists():
                logger.warning(f"Voice models config file does not exist: {config_file}")
                return voices

            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            for voice_config in config_data.get("voices", []):
                name = voice_config.get("name", "")
                url = voice_config.get("url", "")
                
                if not name or not url:
                    logger.warning(f"Invalid voice config entry: {voice_config}")
                    continue
                
                # Convert relative URLs to absolute URLs
                if not url.startswith(("http://", "https://")):
                    audio_url = f"{settings.BASE_URL}/{url}"
                else:
                    audio_url = url
                
                voices.append(VoiceModel(name=name, audio_url=audio_url))
            
            logger.info(f"===== Available voices retrieved successfully: {voices} =====")

            return ServiceResponse(
                status="COMPLETED",
                message="Voice models loaded successfully",
                data=voices
            )
        except Exception as e:
            logger.error(f"===== Error reading voice models config: {str(e)} =====")
            # Fail gracefully with empty list; caller can decide how to respond
            return ServiceResponse(
                status="FAILED",
                message="Error reading voice models config",
                data=voices
            )
