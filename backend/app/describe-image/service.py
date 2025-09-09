"""
Service for image description using AI models.
"""
import logging
from typing import TypeVar

from .schemas import DescribeImageRequest, ServiceResponse
from .adapters.factory import ImageDescriptionAdapterFactory

logger = logging.getLogger(__name__)

T = TypeVar('T')

# No se requiere una función auxiliar ya que usaremos directamente la clase ServiceResponse


async def describe_image(
    request: DescribeImageRequest
) -> ServiceResponse:
    """
    Describe an image using the preloaded adapter.
    
    Args:
        request: The image description request containing image_url and optional prompt
        
    Returns:
        ServiceResponse: A standardized JSON response with status, message, and data
    """
    try:
        logger.info(f"Generating description for image: {request.image_url}")
        adapter = ImageDescriptionAdapterFactory.get_adapter(request.model)
        
        # Delegate to adapter which now handles formatting
        result = await adapter.describe_image(request.image_url, request.prompt)
        
        return ServiceResponse(
            status="success",
            message="Image description generated successfully",
            data=result
        )
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error describing image with {request.model}: {error_msg}")
        
        return ServiceResponse(
            status="error",
            message=f"Service error: {error_msg}",
            data=None
        )

async def warmup(model_name: str) -> ServiceResponse:
    """
    Warmup a specific adapter using the factory pattern.
    
    Args:
        model_name: Name of the model/adapter to warmup
    
    Returns:
        ServiceResponse: A standardized JSON response with status, message, and data
    """
    try:
        adapter = ImageDescriptionAdapterFactory.get_adapter(model_name)
        result = await adapter.warmup()
        
        return ServiceResponse(
            status="success",
            message="Model warmup completed successfully",
            data=result
        )
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Warmup failed for {model_name}: {error_msg}")
        
        return ServiceResponse(
            status="error",
            message=f"Warmup failed for {model_name}: {error_msg}",
            data=None
        )

async def status(model_name: str, job_id: str = None) -> dict:
    """
    Check status of a specific adapter using the factory pattern.
    
    Args:
        model_name: Name of the model/adapter to check status for
        job_id: Optional job ID for status check
    
    Returns:
        dict: Status information with structure like {"status": "COMPLETED", "detail": {...}}
    """
    try:
        adapter = ImageDescriptionAdapterFactory.get_adapter(model_name)
        
        # Check if adapter has status method (currently only Qwen)
        if hasattr(adapter, 'status'):
            result = await adapter.status(job_id or "status-check")
            return result
        else:
            # For adapters without status method, create a basic response
            return {
                "status": "COMPLETED",
                "detail": {
                    "status": "IDLE",
                    "message": f"{model_name} adapter is available (no status endpoint)",
                    "data": ""
                }
            }
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Status check failed for {model_name}: {error_msg}")
        
        # Error response en el mismo formato que las respuestas exitosas
        return {
            "status": "ERROR",
            "detail": {
                "status": "ERROR",
                "message": f"Status check failed for {model_name}: {error_msg}",
                "data": ""
            }
        }


async def get_available_models() -> ServiceResponse:
    """
    Get information about available models.
    
    Returns:
        dict: A standardized JSON response with status, message, and data containing the list of available models
    """
    try:
        models = ImageDescriptionAdapterFactory.list_available_models()
        return ServiceResponse(
            status="success",
            message="Available models retrieved successfully",
            data=models
        )
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error retrieving available models: {error_msg}")
        return ServiceResponse(
            status="error",
            message=f"Error retrieving available models: {error_msg}",
            data=None
        )
