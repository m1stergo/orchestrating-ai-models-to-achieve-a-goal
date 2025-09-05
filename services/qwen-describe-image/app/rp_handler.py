import logging
from typing import Any, Dict

import runpod
from .service import warmup_model, get_service_status, describe_image
from .schemas import DescribeImageRequest
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------- #
#                               Inference Runner                               #
# ---------------------------------------------------------------------------- #

def run_model(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check model status and run inference if ready.
    Uses the same service logic as FastAPI.
    """
    try:
        # Parse input
        input_data = event.get("input", {})
        image_url = input_data.get("image_url")
        prompt = input_data.get("prompt")
        
        if not image_url:
            return {
                "status": "error",
                "message": "image_url is required"
            }
        
        # Create request object
        request = DescribeImageRequest(
            action="inference",
            image_url=image_url,
            prompt=prompt
        )
        
        # Use service function directly
        result = describe_image(request)
        
        # Convert to dict for RunPod response
        return {
            "status": result.status,
            "description": result.description,
            "message": result.message
        }
        
    except Exception as e:
        logger.error(f"Inference failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Inference failed: {str(e)}"
        }

# ---------------------------------------------------------------------------- #
#                               RunPod Handler                                 #
# ---------------------------------------------------------------------------- #

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main RunPod handler that routes requests based on action parameter.
    
    Actions:
    - warmup: Trigger model loading
    - status: Check model status
    - inference: Run image description (default)
    """
    action = event.get("input", {}).get("action", "inference")
    
    logger.info(f"RunPod handler called with action: {action}")
    
    try:
        if action == "warmup":
            return warmup_model()
        elif action == "status":
            return get_service_status()
        elif action == "inference":
            return run_model(event)
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}. Valid actions: warmup, status, inference"
            }
    except Exception as exc:
        logger.error(f"Handler error: {str(exc)}")
        return {
            "status": "error",
            "message": str(exc)
        }


if __name__ == "__main__":
    logger.info("Starting RunPod serverless handler...")
    runpod.serverless.start({"handler": handler})