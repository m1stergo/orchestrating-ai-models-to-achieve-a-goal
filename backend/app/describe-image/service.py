"""
Service for image description using AI models.
"""
import logging
from typing import List

from schemas import DescribeImageRequest, DescribeImageResponse
from adapters.factory import ImageDescriptionAdapterFactory

logger = logging.getLogger(__name__)


async def describe_image(
    request: DescribeImageRequest
) -> DescribeImageResponse:
    """
    Describe an image using the preloaded adapter with concurrency control.
    
    Args:
        request: The image description request containing image_url and optional prompt
        
    Returns:
        DescribeImageResponse: The image description result
    """
    try:
        # Get the correct adapter for image description
        adapter = ImageDescriptionAdapterFactory.get_adapter(request.model)
        
        # Use the adapter's describe_image method
        result = await adapter.describe_image(request.image_url, request.prompt)
        logger.info("Image description completed successfully")
        return DescribeImageResponse(description=result)
    except Exception as e:
        logger.error(f"Error describing image: {str(e)}")
        raise Exception(f"Image description failed: {str(e)}")


async def get_available_models() -> List[str]:
    """
    Get information about available models.
    
    Returns:
        List of available model names
    """
    return ImageDescriptionAdapterFactory.list_available_models()
