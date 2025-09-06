import logging
import time
import uuid
from typing import Any, Dict

import runpod
from .service import warmup_model, describe_image
from .schemas import DescribeImageResponse

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
    start_time = time.time()
    job_id = str(uuid.uuid4()) + "-u1"
    action = event.get("input", {}).get("action", "inference")
    
    logger.info(f"======== RunPod handler called with action: {action} ========")
    
    try:
        if action == "warmup":
            result = warmup_model()
            execution_time = int((time.time() - start_time) * 1000)
            
            return {
                "id": job_id,
                "status": "COMPLETED",
                "delayTime": 0,
                "executionTime": execution_time,
                "workerId": "qwen-worker",
                "output": {
                    "status": result.status,
                    "message": result.message,
                    "data": result.data
                }
            }
            
        elif action == "inference":
            image_url = event.get("input", {}).get("image_url")
            prompt = event.get("input", {}).get("prompt")
            result = describe_image(image_url=image_url, prompt=prompt)
            execution_time = int((time.time() - start_time) * 1000)
            
            return {
                "id": job_id,
                "status": "COMPLETED",
                "delayTime": 0,
                "executionTime": execution_time,
                "workerId": "qwen-worker",
                "output": {
                    "status": result.status,
                    "message": result.message,
                    "data": result.data
                }
            }
            
        else:
            execution_time = int((time.time() - start_time) * 1000)
            return {
                "id": job_id,
                "status": "COMPLETED",
                "delayTime": 0,
                "executionTime": execution_time,
                "workerId": "qwen-worker",
                "output": {
                    "status": "error",
                    "message": f"Unknown action: {action}. Valid actions: warmup, inference",
                    "data": ""
                }
            }
            
    except Exception as exc:
        execution_time = int((time.time() - start_time) * 1000)
        logger.error(f"======== Handler error: {str(exc)} ========")
        
        return {
            "id": job_id,
            "status": "COMPLETED",
            "delayTime": 0,
            "executionTime": execution_time,
            "workerId": "qwen-worker",
            "output": {
                "status": "error",
                "message": str(exc),
                "data": ""
            }
        }


if __name__ == "__main__":
    logger.info("======== Starting RunPod serverless handler... ========")
    runpod.serverless.start({"handler": handler})