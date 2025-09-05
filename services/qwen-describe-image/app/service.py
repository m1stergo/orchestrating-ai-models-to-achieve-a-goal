import logging
import time
import torch
from enum import Enum

from .schemas import DescribeImageRequest, DescribeImageResponse
from .shared import model_instance, model_loaded

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------- #
#                               Model States                                   #
# ---------------------------------------------------------------------------- #

class ModelState(Enum):
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"

# Global state management (shared with RunPod handler)
current_state = ModelState.NOT_LOADED
loading_start_time = None
error_message = None


def describe_image(request: DescribeImageRequest) -> DescribeImageResponse:
    """
    Describe an image using the preloaded adapter.
    Only works if model is in READY state.
    
    Args:
        request: The image description request containing image_url and optional prompt
        
    Returns:
        DescribeImageResponse: The image description result
    """
    global current_state
    
    # Check if model is ready
    if current_state != ModelState.READY:
        return DescribeImageResponse(
            status="error",
            message=f"Model not ready. Current state: {current_state.value}. Call warmup first.",
            description=""
        )
    
    try:
        logger.info(f"Processing image from URL: {request.image_url}")
        result = model_instance.describe_image(request.image_url, request.prompt)
        logger.info("Image description completed successfully")
        
        return DescribeImageResponse(
            status="success",
            description=result
        )
        
    except Exception as e:
        logger.error(f"Inference failed: {str(e)}")
        return DescribeImageResponse(
            status="error",
            message=f"Inference failed: {str(e)}",
            description=""
        )

def warmup_model():
    """
    Trigger model loading (warmup). Should be called first.
    
    Returns:
        dict: Status of the warmup operation
    """
    global current_state, loading_start_time, error_message
    
    if current_state == ModelState.READY:
        return {
            "status": "success",
            "message": "Model already loaded and ready",
            "state": current_state.value
        }
    
    if current_state == ModelState.LOADING:
        elapsed = time.time() - loading_start_time if loading_start_time else 0
        return {
            "status": "loading",
            "message": f"Model is currently loading... ({elapsed:.1f}s elapsed)",
            "state": current_state.value,
            "elapsed_seconds": elapsed
        }
    
    # Start loading
    current_state = ModelState.LOADING
    loading_start_time = time.time()
    error_message = None
    
    logger.info("Starting model warmup...")
    
    try:
        model_instance.load_model()
        current_state = ModelState.READY
        total_time = time.time() - loading_start_time
        
        logger.info(f"Model warmup completed successfully in {total_time:.1f}s")
        return {
            "status": "success",
            "message": f"Model loaded successfully in {total_time:.1f}s",
            "state": current_state.value,
            "loading_time_seconds": total_time
        }
        
    except Exception as e:
        current_state = ModelState.ERROR
        error_message = str(e)
        logger.error(f"Model warmup failed: {error_message}")
        
        return {
            "status": "error",
            "message": f"Failed to load model: {error_message}",
            "state": current_state.value,
            "error": error_message
        }

def get_service_status():
    """
    Check current model status without triggering loading.
    
    Returns:
        dict: Current model state and status information
    """
    global current_state, loading_start_time, error_message
    
    response = {
        "state": current_state.value,
    }
    
    if current_state == ModelState.LOADING and loading_start_time:
        elapsed = time.time() - loading_start_time
        response.update({
            "status": "loading",
            "message": f"Model is loading... ({elapsed:.1f}s elapsed)",
            "elapsed_seconds": elapsed
        })
    elif current_state == ModelState.READY:
        response.update({
            "status": "ready",
            "message": "Model is ready for inference"
        })
    elif current_state == ModelState.ERROR:
        response.update({
            "status": "error",
            "message": f"Model failed to load: {error_message}",
            "error": error_message
        })
    else:
        response.update({
            "status": "not_loaded",
            "message": "Model not loaded. Call warmup first."
        })
    
    return response
