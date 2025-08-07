"""
Service for text generation using AI models.
"""
import logging
import asyncio
from typing import List

from schemas import GenerateDescriptionRequest, GenerateDescriptionResponse
from adapters.factory import TextGenerationAdapterFactory

logger = logging.getLogger(__name__)

# Semaphore to limit concurrent inference requests
# Adjust the value based on your GPU memory and model requirements
MAX_CONCURRENT_INFERENCES = 1
semaphore = asyncio.Semaphore(MAX_CONCURRENT_INFERENCES)


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
        # Get the correct adapter for text generation
        adapter = TextGenerationAdapterFactory.get_adapter(request.model)
        
        # Use semaphore to limit concurrent inferences
        async with semaphore:
            # Use the adapter's generate_text method
            result = await adapter.generate_text(request.text, request.prompt)
        logger.info("Text generation completed successfully")
        return GenerateDescriptionResponse(text=result)
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
