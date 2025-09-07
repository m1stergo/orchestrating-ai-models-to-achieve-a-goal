import logging
from typing import Any, Dict

import runpod
from .service import warmup_model, describe_image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------- #
#                               RunPod Handler                                 #
# ---------------------------------------------------------------------------- #

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main RunPod handler that routes requests based on action parameter.
    
    Actions:
    - warmup: Trigger model loading
    - inference: Run image description (default)
    """
    action = event.get("input", {}).get("action", "inference")
    
    logger.info(f"======== RunPod handler called with action: {action} ========")
    
    try:
        if action == "warmup":
            result = warmup_model()
            
            return {
                "status": result.status,
                "message": result.message,
                "data": result.data
            }
            
        elif action == "inference":
            image_url = event.get("input", {}).get("image_url")
            prompt = event.get("input", {}).get("prompt")
            result = describe_image(image_url=image_url, prompt=prompt)
            
            return {
                "status": result.status,
                "message": result.message,
                "data": result.data
            }
            
        else:
            return {
                "status": "ERROR",
                "message": f"Unknown action: {action}. Valid actions: warmup, inference",
                "data": ""
            }
            
    except Exception as exc:
        logger.error(f"======== Handler error: {str(exc)} ========")
        
        return {
            "status": "ERROR",
            "message": str(exc),
            "data": ""
        }


if __name__ == "__main__":
    logger.info("======== Starting RunPod serverless handler... ========")
    runpod.serverless.start({"handler": handler})