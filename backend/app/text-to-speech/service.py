"""
Service for text-to-speech generation using TTS models.
"""
import logging
import json
import uuid
import os
from typing import List
from pathlib import Path

from .schemas import TextToSpeechRequest, TextToSpeechResponse, VoiceModel
from .adapters.factory import TextToSpeechAdapterFactory
from app.config import settings

logger = logging.getLogger(__name__)

async def save_generated_audio(audio_bytes: bytes) -> dict:
    """
    Saves generated audio bytes to the audio directory.
    
    Args:
        audio_bytes: The audio data as bytes
        
    Returns:
        A dictionary with information about the saved file
    """
    # Ensure the directory exists
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)
    
    # Generate a unique filename
    unique_filename = f"{uuid.uuid4()}.wav"
    file_path = settings.AUDIO_DIR / unique_filename
    
    # Save the file
    with open(file_path, "wb") as buffer:
        buffer.write(audio_bytes)
    
    # Calculate the absolute URL to access the audio
    audio_url = f"{settings.audio_url}/{unique_filename}"
    
    return {
        "filename": unique_filename,
        "content_type": "audio/wav",
        "audio_url": audio_url,
        "size": os.path.getsize(file_path)
    }

async def generate_speech(
    request: TextToSpeechRequest
) -> TextToSpeechResponse:
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
        audio_bytes = await adapter.inference(request.text, request.voice_url)
        
        # Save the audio bytes to file and get the URL
        audio_info = await save_generated_audio(audio_bytes)
        logger.info("Speech generation completed successfully")
        
        return TextToSpeechResponse(
            audio_url=audio_info["audio_url"]
        )
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        raise Exception(f"Speech generation failed: {str(e)}")


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
