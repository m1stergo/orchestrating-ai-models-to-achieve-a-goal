import logging
import asyncio

from schemas import GenerateDescriptionRequest, GenerateDescriptionResponse

logger = logging.getLogger(__name__)

# Global model instance (shared with main.py)
from main import model_instance, model_loaded

# Semaphore to limit concurrent inference requests
# Adjust the value based on your GPU memory and model requirements
MAX_CONCURRENT_INFERENCES = 1
semaphore = asyncio.Semaphore(MAX_CONCURRENT_INFERENCES)

# Hardcoded prompt template
PROMPT_TEMPLATE = """
You are a professional e-commerce copywriter. Write a compelling product description based on the information below.

{text}

Write a clear, persuasive, English description of the product.
"""


async def generate_description(
    request: GenerateDescriptionRequest
) -> GenerateDescriptionResponse:
    """
    Generate description using the preloaded Mistral model with concurrency control.
    
    Args:
        request: The generation request containing text and optional prompt
        
    Returns:
        Generated description response
    """
    global model_instance, model_loaded
    
    try:
        # Check if model is loaded
        if not model_loaded:
            logger.warning("Model not loaded yet, attempting to load")
            try:
                await model_instance.is_loaded()
                model_loaded = True
            except Exception as e:
                logger.error(f"Failed to load model on demand: {str(e)}")
                return GenerateDescriptionResponse(text="Model not loaded and failed to load on demand")
        
        # Format the prompt with request data
        prompt = request.prompt if request.prompt else PROMPT_TEMPLATE.format(text=request.text)
        
        # Use semaphore to limit concurrent inferences
        async with semaphore:
            logger.info(f"Processing text generation request")
            # Generate description using the preloaded model instance
            result = await model_instance.generate_description(
                text=request.text,
                prompt=prompt
            )
        
        logger.info("Text generation completed successfully")
        return GenerateDescriptionResponse(text=result)
        
    except Exception as e:
        logger.error(f"Error generating description: {str(e)}")
        raise Exception(f"Text generation failed: {str(e)}")