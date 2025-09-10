"""
Service for text generation using AI models.
"""
import logging

from app.shared.schemas import GenerateDescriptionRequest, ServiceResponse
from .adapters.factory import GenerateDescriptionAdapterFactory

logger = logging.getLogger(__name__)

async def inference_text(
    request: GenerateDescriptionRequest
) -> ServiceResponse:
    """
    Generate description using the selected adapter with concurrency control.
    
    Args:
        request: The generation request containing text and optional prompt
        
    Returns:
        ServiceResponse: The generated description result
    """
    try:
        logger.info(f"Generating description for text: {request.text}")
        adapter = GenerateDescriptionAdapterFactory.get_adapter(request.model)
        result = await adapter.inference_text(request.text, request.prompt, request.categories)
        logger.info("Text generation completed successfully")
        return ServiceResponse(
            status="success", 
            message="Text generation completed successfully", 
            data=result
        )
    except Exception as e:
        logger.error(f"Error generating description: {str(e)}")
        raise Exception(f"Text generation failed: {str(e)}")


async def inference_promotional_audio_script(
    request: GenerateDescriptionRequest
) -> ServiceResponse:
    """
    Generate promotional audio script using the selected adapter with concurrency control.
    
    Args:
        request: The promotional audio script generation request containing text and optional model
        
    Returns:
        ServiceResponse: The generated promotional audio script result
    """
    try:
        logger.info(f"Generating promotional audio script for text: {request.text[:50]}...")
        adapter = GenerateDescriptionAdapterFactory.get_adapter(request.model)
        result = await adapter.inference_promotional_audio(request.text, request.prompt)
        logger.info("Promotional audio script generation completed successfully")
        return ServiceResponse(status="success", message="Promotional audio script generated successfully", data=result)
    except Exception as e:
        logger.error(f"Error generating promotional audio script: {str(e)}")
        raise Exception(f"Promotional audio script generation failed: {str(e)}")

async def warmup(model_name: str) -> ServiceResponse:
    """
    Warmup a specific adapter using the factory pattern.
    
    Args:
        model_name: Name of the model/adapter to warmup
    
    Returns:
        ServiceResponse with warmup status for the adapter
    """
    try:
        adapter = GenerateDescriptionAdapterFactory.get_adapter(model_name)
        result = await adapter.warmup()

        return ServiceResponse(
            status=result.get('status', 'success'),
            message=result.get('message', f'{model_name} adapter is ready'),
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

async def get_available_models() -> ServiceResponse:
    """
    Get information about available models.
    
    Returns:
        dict: A standardized JSON response with status, message, and data containing the list of available models
    """
    try:
        models = GenerateDescriptionAdapterFactory.list_available_models()
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