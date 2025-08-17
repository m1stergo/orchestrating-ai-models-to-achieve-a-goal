"""
Service for text-to-speech generation using TTS models.
"""
import logging
from typing import List

from .schemas import TextToSpeechRequest, TextToSpeechResponse
from .adapters.factory import TextToSpeechAdapterFactory

logger = logging.getLogger(__name__)

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
        result = await adapter.generate_speech(request.text, request.audio_prompt_url)
        logger.info("Speech generation completed successfully")
        
        return TextToSpeechResponse(
            audio_url=result.get("audio_url")
        )
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        raise Exception(f"Speech generation failed: {str(e)}")


async def get_available_models() -> List[str]:
    """
    Get information about available TTS models.
    
    Returns:
        List of available model names
    """
    return TextToSpeechAdapterFactory.list_available_models()
