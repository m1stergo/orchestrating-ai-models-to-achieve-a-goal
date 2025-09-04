import os
import time
import logging
from typing import Any, Dict

import runpod
from app.shared import model_instance, model_loaded

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------- #
#                               Model Preloader                               #
# ---------------------------------------------------------------------------- #

def preload_model():
    """Preload the model at startup, similar to FastAPI lifespan."""
    global model_instance
    
    logger.info("Starting model preloading for RunPod...")
    try:
        model_instance.load_model()
        logger.info("Model preloaded successfully for RunPod")
        return True
    except Exception as e:
        logger.error(f"Failed to preload model: {str(e)}")
        return False


# ---------------------------------------------------------------------------- #
#                               Inference Runner                               #
# ---------------------------------------------------------------------------- #

def run_model(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check model status and run inference if ready.
    Uses existing FastAPI service logic.
    """
    from app.service import describe_image
    from app.schemas import DescribeImageRequest, DescribeImageResponse
    
    try:
        # Parse input
        input_data = event.get("input", {})
        image_url = input_data.get("image_url")
        prompt = input_data.get("prompt")
        
        if not image_url:
            return {
                "status": "error",
                "error": "image_url is required"
            }
        
        # Create request object (reusing FastAPI schema)
        request = DescribeImageRequest(
            image_url=image_url,
            prompt=prompt
        )
        
        # Use existing service logic
        response = describe_image(request)
        
        return {
            "status": "success",
            "description": response.description
        }
        
    except Exception as e:
        logger.error(f"Error in run_model: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


# ---------------------------------------------------------------------------- #
#                                RunPod Handler                                #
# ---------------------------------------------------------------------------- #

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    RunPod serverless handler. RunPod will pass an `event` dict with an `input` key.
    Return value must be JSON-serializable.
    """
    try:
        return run_model(event)
    except Exception as exc:  # make sure exceptions are visible to RunPod logs
        return {
            "status": "error",
            "error": str(exc),
        }


if __name__ == "__main__":
    logger.info("Starting RunPod serverless handler...")
    runpod.serverless.start({"handler": handler})