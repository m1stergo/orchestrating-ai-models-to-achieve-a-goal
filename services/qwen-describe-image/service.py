import logging
import asyncio

from schemas import DescribeImageRequest, DescribeImageResponse

logger = logging.getLogger(__name__)

# Import the global model instance from main.py
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
                return DescribeImageResponse(description="Model not loaded and failed to load on demand")
        
        # Use semaphore to limit concurrent inferences
        async with semaphore:
            logger.info(f"Processing image from URL: {request.image_url}")
            # Use the global model instance
            result = await model_instance.describe_image(request.image_url, request.prompt)
        logger.info("Image description completed successfully")
        return DescribeImageResponse(description=result)
    except Exception as e:
        logger.error(f"Error describing image: {str(e)}")
        raise Exception(f"Image description failed: {str(e)}")
