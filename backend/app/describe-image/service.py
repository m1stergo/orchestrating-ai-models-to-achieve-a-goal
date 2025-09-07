"""
Service for image description using AI models.
"""
import logging
from typing import List

from .schemas import DescribeImageRequest, StandardResponse
from .adapters.factory import ImageDescriptionAdapterFactory

logger = logging.getLogger(__name__)


async def describe_image(
    request: DescribeImageRequest
) -> StandardResponse:
    """
    Describe an image using the preloaded adapter.
    
    Args:
        request: The image description request containing image_url and optional prompt
        
    Returns:
        StandardResponse: A standardized response with status, id, and details
    """
    try:
        logger.info(f"Generating description for image: {request.image_url}")
        adapter = ImageDescriptionAdapterFactory.get_adapter(request.model)
        
        # Delegate to adapter which now handles formatting
        return await adapter.describe_image(request.image_url, request.prompt)
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error describing image with {request.model}: {error_msg}")
        
        # Create a generic error response when adapter call fails completely
        adapter = ImageDescriptionAdapterFactory.get_adapter(request.model)
        return adapter.format_error(f"Service error: {error_msg}")

async def warmup(model_name: str) -> StandardResponse:
    """
    Warmup a specific adapter using the factory pattern.
    
    Args:
        model_name: Name of the model/adapter to warmup
    
    Returns:
        StandardResponse with warmup status for the adapter
    """
    try:
        adapter = ImageDescriptionAdapterFactory.get_adapter(model_name)
        return await adapter.warmup()
        
    except Exception as e:
        logger.error(f"Warmup failed for {model_name}: {str(e)}")
        adapter = ImageDescriptionAdapterFactory.get_adapter(model_name)
        return adapter.format_error(f"Warmup failed for {model_name}: {str(e)}")

async def status(model_name: str, job_id: str = None) -> StandardResponse:
    """
    Check status of a specific adapter using the factory pattern.
    
    Args:
        model_name: Name of the model/adapter to check status for
        job_id: Optional job ID for status check
    
    Returns:
        StandardResponse with status information for the adapter
    """
    try:
        adapter = ImageDescriptionAdapterFactory.get_adapter(model_name)
        
        # Check if adapter has status method (currently only Qwen)
        if hasattr(adapter, 'status'):
            return await adapter.status(job_id or "status-check")
        else:
            # For adapters without status method, create a basic response
            return adapter.format_response(
                status="COMPLETED",
                detail_status="SUCCESS",
                detail_message=f"{model_name} adapter is available (no status endpoint)"
            )
            
    except Exception as e:
        logger.error(f"Status check failed for {model_name}: {str(e)}")
        adapter = ImageDescriptionAdapterFactory.get_adapter(model_name)
        return adapter.format_error(f"Status check failed for {model_name}: {str(e)}")


async def get_available_models() -> List[str]:
    """
    Get information about available models.
    
    Returns:
        List of available model names
    """
    return ImageDescriptionAdapterFactory.list_available_models()
