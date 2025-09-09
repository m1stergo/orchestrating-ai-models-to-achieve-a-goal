"""
Service for text generation using AI models.
"""
import logging
import aiohttp
from typing import List
from app.config import settings

from .schemas import GenerateDescriptionRequest, ServiceResponse, GeneratePromotionalAudioScriptRequest
from .adapters.factory import TextGenerationAdapterFactory

logger = logging.getLogger(__name__)

async def generate_description(
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
        adapter = TextGenerationAdapterFactory.get_adapter(request.model)
        result = await adapter.generate_text(request.text, request.prompt, request.categories)
        logger.info("Text generation completed successfully")
        return ServiceResponse(status="success", message="Text generation completed successfully", data=result)
    except Exception as e:
        logger.error(f"Error generating description: {str(e)}")
        raise Exception(f"Text generation failed: {str(e)}")


async def generate_promotional_audio_script(
    request: GeneratePromotionalAudioScriptRequest
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
        adapter = TextGenerationAdapterFactory.get_adapter(request.model)
        result = await adapter.generate_promotional_audio_script(request.text, request.prompt)
        logger.info("Promotional audio script generation completed successfully")
        return ServiceResponse(status="success", message="Promotional audio script generated successfully", data=result)
    except Exception as e:
        logger.error(f"Error generating promotional audio script: {str(e)}")
        raise Exception(f"Promotional audio script generation failed: {str(e)}")


async def warmup_mistral_service() -> dict:
    """
    Warmup the Mistral service by calling its warmup endpoint.
    
    Returns:
        Dict with warmup status and information
    """
    try:
        timeout = aiohttp.ClientTimeout(total=10)  # Short timeout for warmup call
        async with aiohttp.ClientSession(timeout=timeout) as session:
            warmup_url = f"{settings.GENERATE_DESCRIPTION_MISTRAL_URL}/warmup"
            
            async with session.get(warmup_url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    logger.info(f"Mistral warmup successful: {result}")
                    return {
                        "status": "success",
                        "message": "Mistral service warmup initiated successfully",
                        "detail": result
                    }
                else:
                    error_text = await resp.text()
                    logger.error(f"Mistral warmup failed: {resp.status}, {error_text}")
                    return {
                        "status": "error",
                        "message": f"Warmup failed with status {resp.status}",
                        "detail": error_text
                    }
                    
    except aiohttp.ClientError as e:
        logger.error(f"Mistral warmup connection error: {str(e)}")
        return {
            "status": "error",
            "message": "Could not connect to Mistral service",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Mistral warmup error: {str(e)}")
        return {
            "status": "error", 
            "message": "Warmup failed",
            "detail": str(e)
        }


async def warmup_service(model_name: str) -> ServiceResponse[dict]:
    """
    Warmup a specific adapter using the factory pattern.
    
    Args:
        model_name: Name of the model/adapter to warmup
    
    Returns:
        ServiceResponse with warmup status for the adapter
    """
    try:
        adapter = TextGenerationAdapterFactory.get_adapter(model_name)
        result = await adapter.warmup()
        logger.info(f"Warmup completed for {model_name}: {result['status']}")
        # Return formatted ServiceResponse
        return ServiceResponse(
            status=result.get('status', 'success'),
            message=result.get('message', f'{model_name} adapter is ready'),
            data=result
        )
    except Exception as e:
        logger.error(f"Warmup failed for {model_name}: {str(e)}")
        # Return error ServiceResponse
        return ServiceResponse(
            status="error",
            message=f"Warmup failed for {model_name}",
            data={"detail": str(e)}
        )


async def status_service(model_name: str) -> ServiceResponse[dict]:
    """
    Check health status of a specific adapter using the factory pattern.
    
    Args:
        model_name: Name of the model/adapter to check
    
    Returns:
        ServiceResponse with health status for the adapter
    """
    try:
        adapter = TextGenerationAdapterFactory.get_adapter(model_name)
        result = await adapter.status()
        logger.info(f"Health check completed for {model_name}: {result['status']}")
        # Return formatted ServiceResponse
        return ServiceResponse(
            status=result.get('status', 'success'),
            message=result.get('message', f'{model_name} status checked'),
            data=result
        )
    except Exception as e:
        logger.error(f"Health check failed for {model_name}: {str(e)}")
        # Return error ServiceResponse
        return ServiceResponse(
            status="error",
            message=f"Health check failed for {model_name}",
            data={"status": "unhealthy", "detail": str(e)}
        )


async def get_available_models() -> List[str]:
    """
    Get information about available models.
    
    Returns:
        List of available model names
    """
    return TextGenerationAdapterFactory.list_available_models()
