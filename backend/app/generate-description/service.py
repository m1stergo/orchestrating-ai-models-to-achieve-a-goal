"""
Service for text generation using AI models.
"""
import logging
from typing import List

from .schemas import GenerateDescriptionRequest, GenerateDescriptionResponse, GeneratePromotionalAudioScriptRequest, GeneratePromotionalAudioScriptResponse
from .adapters.factory import TextGenerationAdapterFactory

logger = logging.getLogger(__name__)

async def generate_description(
    request: GenerateDescriptionRequest
) -> GenerateDescriptionResponse:
    """
    Generate description using the selected adapter with concurrency control.
    
    Args:
        request: The generation request containing text and optional prompt
        
    Returns:
        GenerateDescriptionResponse: The generated description result
    """
    try:
        logger.info(f"Generating description for text: {request.text}")
        adapter = TextGenerationAdapterFactory.get_adapter(request.model)
        result = await adapter.generate_text(request.text, request.prompt)
        logger.info("Text generation completed successfully")
        return GenerateDescriptionResponse(description=result)
    except Exception as e:
        logger.error(f"Error generating description: {str(e)}")
        raise Exception(f"Text generation failed: {str(e)}")


async def generate_promotional_audio_script(
    request: GeneratePromotionalAudioScriptRequest
) -> GeneratePromotionalAudioScriptResponse:
    """
    Generate promotional audio script using the selected adapter with concurrency control.
    
    Args:
        request: The promotional audio script generation request containing text and optional model
        
    Returns:
        GeneratePromotionalAudioScriptResponse: The generated promotional audio script result
    """
    try:
        logger.info(f"Generating promotional audio script for text: {request.text[:50]}...")
        adapter = TextGenerationAdapterFactory.get_adapter(request.model)
        result = await adapter.generate_promotional_audio_script(request.text)
        logger.info("Promotional audio script generation completed successfully")
        return GeneratePromotionalAudioScriptResponse(text=result)
    except Exception as e:
        logger.error(f"Error generating promotional audio script: {str(e)}")
        raise Exception(f"Promotional audio script generation failed: {str(e)}")


async def get_available_models() -> List[str]:
    """
    Get information about available models.
    
    Returns:
        List of available model names
    """
    return TextGenerationAdapterFactory.list_available_models()
