import logging

from .schemas import GenerateAudioRequest
from .shared import model_instance, model_loaded

logger = logging.getLogger(__name__)


def generate_audio(request: GenerateAudioRequest) -> bytes:
    """
    Generate audio from text using the TTS model.
    
    Args:
        request: The audio generation request containing text and optional audio_prompt_path
        
    Returns:
        bytes: The generated audio as WAV bytes
    """
    global model_instance, model_loaded
    
    try:
        # Check if model is loaded
        if not model_loaded:
            logger.warning("Model not loaded yet, attempting to load")
            try:
                model_instance.is_loaded()
                model_loaded = True
            except Exception as e:
                logger.error(f"Failed to load model on demand: {str(e)}")
                raise Exception("Model not loaded and failed to load on demand")
        
        logger.info(f"Generating audio for text: {request.text}")
        # Use the global model instance
        result = model_instance.generate_audio(request.text, request.audio_prompt_url)
        logger.info("Audio generation completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise Exception(f"Audio generation failed: {str(e)}")
