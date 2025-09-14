import logging
import runpod
from typing import Any, Dict
from .shared import handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------- #
#                               RunPod Handler                                 #
# ---------------------------------------------------------------------------- #

def rp_handler(event: Dict[str, Any]) -> Dict[str, Any]:
    input_data = event.get("input", {})
    logger.info(f"======== Received RunPod event with input: {input_data} ========")
    
    response = handler.run_job(input_data)
    
    if hasattr(response, "dict"):
        return response.dict()
    elif hasattr(response, "model_dump"):
        return response.model_dump()
    else:
        return response


if __name__ == "__main__":
    logger.info("======== Starting RunPod serverless handler... ========")
    runpod.serverless.start({"handler": rp_handler})