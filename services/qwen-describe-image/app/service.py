import logging
import time

from .schemas import DescribeImageRequest, DescribeImageResponse
from .shared import model_instance
from .model import ModelState

logger = logging.getLogger(__name__)

def describe_image(request: DescribeImageRequest = None, image_url: str = None, prompt: str = None) -> DescribeImageResponse:
    """
    Describe an image using the preloaded adapter.
    Only works if model is in IDDLE state.
    
    Args:
        request: The image description request containing image_url and optional prompt
        image_url: URL of the image to describe (alternative to request)
        prompt: Optional prompt to guide the description (alternative to request)
        
    Returns:
        DescribeImageResponse: The image description result
    """
    # Handle both request object and individual parameters
    if request is not None:
        actual_image_url = request.image_url
        actual_prompt = request.prompt
    else:
        actual_image_url = image_url
        actual_prompt = prompt
    
    # Check if model is ready using model's state
    if model_instance.state == ModelState.COLD:
        return DescribeImageResponse(
            status="error",
            message=f"Model not ready. Current state: {model_instance.state.value}. Call warmup first.",
            data=""
        )

    if model_instance.state == ModelState.LOADING:
        return DescribeImageResponse(
            status="loading",
            message=f"Model is currently loading...",
            data=""
        )
    
    try:
        logger.info(f"======== Processing image from URL: {actual_image_url} ========")
        result = model_instance.describe_image(actual_image_url, actual_prompt)
        logger.info("======== Image description completed successfully ========")
        
        return DescribeImageResponse(
            status="success",
            data=result
        )
        
    except Exception as e:
        logger.error(f"======== Inference failed: {str(e)} ========")
        return DescribeImageResponse(
            status="error",
            message=f"Inference failed: {str(e)}",
            data=""
        )

def warmup_model():
    """
    Trigger model loading (warmup). Should be called first.
    
    Returns:
        DescribeImageResponse: Status of the warmup operation
    """
    if model_instance.state == ModelState.IDDLE:
        return DescribeImageResponse(
            status="success",
            message="Model already loaded and ready",
            data=""
        )
    
    if model_instance.state == ModelState.LOADING:
        return DescribeImageResponse(
            status="loading",
            message=f"Model is currently loading...",
            data=""
        )
    
    logger.info("======== Starting model warmup... ========")
    
    try:
        model_instance.load_model()
        
        logger.info("======== Model warmup executed successfully ========")
        return DescribeImageResponse(
            status="success",
            message="Model warmup executed successfully",
            data=""
        )
        
    except Exception as e:
        logger.error(f"Model warmup failed: {str(e)}")
        
        return DescribeImageResponse(
            status="error",
            message=f"Failed to warmup model: {str(e)}",
            data=""
        )
