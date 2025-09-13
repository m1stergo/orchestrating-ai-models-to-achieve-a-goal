"""
Service for text-to-speech generation using TTS models.
"""
import logging
import json
from typing import List
from pathlib import Path

from .schemas import TextToSpeechRequest, VoiceModel
from .adapters.factory import TextToSpeechAdapterFactory
from app.shared.schemas import ServiceResponse
from app.config import settings

logger = logging.getLogger(__name__)

async def inference(
    request: TextToSpeechRequest
) -> ServiceResponse:
    """
    Generate speech using the selected adapter with concurrency control.
    
    Args:
        request: The TTS request containing text and optional parameters
        
    Returns:
        TextToSpeechResponse: The generated speech result
    """
    try:
        logger.info(f"Generating speech for text: {request.text[:50]}...")
        adapter = TextToSpeechAdapterFactory.get_adapter(request.model)
        audio_url = await adapter.inference(request.text, request.voice_url)
        
        logger.info("Speech generation completed successfully")
        
        return ServiceResponse(
            status="success",
            message="Speech generated successfully",
            data={
                "audio_url": audio_url
            }
        )
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        raise Exception(f"Speech generation failed: {str(e)}")

async def warmup(model_name: str) -> ServiceResponse:
    """
    Warmup a specific adapter using the factory pattern.
    
    Args:
        model_name: Name of the model/adapter to warmup
    
    Returns:
        ServiceResponse: A standardized JSON response with status, message, and data
    """
    try:
        adapter = TextToSpeechAdapterFactory.get_adapter(model_name)
        # La función warmup del adaptador siempre debe retornar un string
        result = await adapter.warmup()
        
        return ServiceResponse(
            status="success",
            message="Model warmup successful",
            data={"message": result}
        )
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Warmup failed for {model_name}: {error_msg}")
        
        return ServiceResponse(
            status="error",
            message=f"Warmup failed for {model_name}: {error_msg}",
            data={"error": error_msg}
        )

async def list_available_voices() -> List[VoiceModel]:
    """
    Read available voice models from JSON configuration file.

    The configuration file contains a list of voice models with name and URL.
    URLs can be relative (will be prefixed with BASE_URL) or absolute.

    Returns:
        List[VoiceModel]: Available voices with name and audio_url.
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
        
        logger.info(f"Loaded {len(voices)} voice models from config")
        logger.info(f"###################### Available voices retrieved successfully: {voices}")

        return voices
    except Exception as e:
        logger.error(f"Error reading voice models config: {str(e)}")
        # Fail gracefully with empty list; caller can decide how to respond
        return voices


async def get_available_models() -> List[str]:
    """
    Get information about available TTS models.
    
    Returns:
        List of available model names
    """
    return TextToSpeechAdapterFactory.list_available_models()
