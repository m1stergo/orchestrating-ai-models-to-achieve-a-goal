"""
Service for image description using AI models.
"""
import logging

from app.shared.schemas import DescribeImageRequest, ServiceResponse
from .adapters.factory import ImageDescriptionAdapterFactory

logger = logging.getLogger(__name__)

# No se requiere una función auxiliar ya que usaremos directamente la clase ServiceResponse


async def inference(
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
        result = await adapter.inference(request.image_url, request.prompt)

        logger.info(f"Description result: {result}")
        
        return ServiceResponse(
            status=result.get("output", {}).get("status", ""),
            message=result.get("output", {}).get("message", ""),
            data=result.get("output", {}).get("data", "")
        )
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error describing image with {request.model}: {error_msg}")
        
        return ServiceResponse(
            status="error",
            message=f"Service error: {error_msg}",
            data=result.get("output", {}).get("data", "")
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
        # La función warmup del adaptador siempre debe retornar un string
        result = await adapter.warmup()

        logger.info(f"Warmup result: {result}")
        
        return ServiceResponse(
            status=result.get("output", {}).get("status", ""),
            message=result.get("output", {}).get("message", ""),
            data=result.get("output", {}).get("data", "")
        )
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Warmup failed for {model_name}: {error_msg}")
        
        return ServiceResponse(
            status="error",
            message=f"Warmup failed for {model_name}: {error_msg}",
            data=None
        )

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
