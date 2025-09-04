import logging
import torch

from .schemas import DescribeImageRequest, DescribeImageResponse
from .shared import model_instance, model_loaded

logger = logging.getLogger(__name__)


def describe_image(request: DescribeImageRequest) -> DescribeImageResponse:
    """
    Describe an image using the preloaded adapter.
    
    Args:
        request: The image description request containing image_url and optional prompt
        
    Returns:
        DescribeImageResponse: The image description result
    """
    global model_instance
    
    try:
        # Check if model is loaded
        if not model_instance.is_loaded():
            logger.warning("Model not loaded yet, attempting to load")
            try:
                model_instance.load_model()
            except Exception as e:
                logger.error(f"Failed to load model on demand: {str(e)}")
                return DescribeImageResponse(description="Model not loaded and failed to load on demand")
        
        logger.info(f"Processing image from URL: {request.image_url}")
        result = model_instance.describe_image(request.image_url, request.prompt)
        logger.info("Image description completed successfully")
        return DescribeImageResponse(description=result)
    except Exception as e:
        logger.error(f"Error describing image: {str(e)}")
        raise Exception(f"Image description failed: {str(e)}")

def warmup_model():
    """
    Trigger model loading if not already loaded.
    Useful for manual warmup after deployment.
    
    Returns:
        dict: Status of the warmup operation
    """
    global model_instance
    
    if model_instance.is_loaded():
        logger.info("Model already loaded")
        return {"status": "already_loaded", "loaded": True}
    
    try:
        logger.info("Starting model warmup...")
        model_instance.load_model()
        
        logger.info("Model warmup completed successfully")
        return {"loaded": True}
    except Exception as e:
        logger.error(f"Model warmup failed: {str(e)}")
        raise Exception(f"Failed to load model: {str(e)}")
