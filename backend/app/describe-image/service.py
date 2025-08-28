"""
Service for image description using AI models.
"""
import logging
import aiohttp
from typing import List

from .schemas import DescribeImageRequest, DescribeImageResponse
from .adapters.factory import ImageDescriptionAdapterFactory
from app.config import settings

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
        logger.info(f"Generating description for image: {request.image_url}")
        adapter = ImageDescriptionAdapterFactory.get_adapter(request.model)
        result = await adapter.describe_image(request.image_url, request.prompt)
        logger.info("Image description completed successfully")
        return DescribeImageResponse(description=result)
    except Exception as e:
        logger.error(f"Error describing image: {str(e)}")
        raise Exception(f"Image description failed: {str(e)}")


async def warmup_qwen_service() -> dict:
    """
    Warmup the Qwen service by calling its warmup endpoint.
    
    Returns:
        Dict with warmup status and information
    """
    try:
        timeout = aiohttp.ClientTimeout(total=10)  # Short timeout for warmup call
        async with aiohttp.ClientSession(timeout=timeout) as session:
            warmup_url = f"{settings.DESCRIBE_IMAGE_QWEN_URL}/warmup"
            
            async with session.get(warmup_url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    logger.info(f"Qwen warmup successful: {result}")
                    return {
                        "status": "success",
                        "message": "Qwen service warmup initiated successfully",
                        "details": result
                    }
                else:
                    error_text = await resp.text()
                    logger.error(f"Qwen warmup failed: {resp.status}, {error_text}")
                    return {
                        "status": "error",
                        "message": f"Warmup failed with status {resp.status}",
                        "details": error_text
                    }
                    
    except aiohttp.ClientError as e:
        logger.error(f"Qwen warmup connection error: {str(e)}")
        return {
            "status": "error",
            "message": "Could not connect to Qwen service",
            "details": str(e)
        }
    except Exception as e:
        logger.error(f"Qwen warmup error: {str(e)}")
        return {
            "status": "error", 
            "message": "Warmup failed",
            "details": str(e)
        }


async def get_available_models() -> List[str]:
    """
    Get information about available models.
    
    Returns:
        List of available model names
    """
    return ImageDescriptionAdapterFactory.list_available_models()
