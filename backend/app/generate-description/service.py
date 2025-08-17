"""
Service for text generation using AI models.
"""
import logging
import asyncio
from typing import List

from .schemas import GenerateDescriptionRequest, GenerateDescriptionResponse
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


async def get_available_models() -> List[str]:
    """
    Get information about available models.
    
    Returns:
        List of available model names
    """
    return TextGenerationAdapterFactory.list_available_models()
