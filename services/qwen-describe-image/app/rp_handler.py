import logging
import runpod
from typing import Any, Dict
from .shared import handler
from .handler import InferenceResponse, InferenceStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------- #
#                               RunPod Handler                                 #
# ---------------------------------------------------------------------------- #

def rp_handler(event: Dict[str, Any]) -> InferenceResponse:
    input_data = event.get("input", {})
    logger.info(f"======== Received RunPod event with input: {input_data} ========")
    
    action = input_data.get("action", "inference");
    
    if action == "inference":
        return handler.infer(input_data)
    elif action == "warmup":
        return handler.load_model()
    else:
        return InferenceResponse(
            status=InferenceStatus.ERROR,
            message="Invalid action",
            data=""
        )


if __name__ == "__main__":
    logger.info("======== Starting RunPod serverless handler... ========")
    runpod.serverless.start({"handler": rp_handler})