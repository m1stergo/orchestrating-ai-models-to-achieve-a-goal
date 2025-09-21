import logging
import runpod
from typing import Any, Dict
from .shared import handler
from .common import InferenceStatus, InferenceResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rp_handler(event: Dict[str, Any]) -> Dict[str, Any]:
    input_data = event.get("input", {})
    logger.info(f"==== Received RunPod event with input: {input_data} ====")
    action = input_data.get("action", "inference")
    try:
        if (handler.is_busy()):
            return InferenceResponse(status=handler.status(), message="Model is currently processing another request. Please try again later.")
        if action == "inference":
            response = handler.infer(input_data)
        elif action == "warmup":
            response = handler.load_model()
        else:
            response = InferenceResponse(status=InferenceStatus.FAILED, message="Invalid action")
        if hasattr(response, "model_dump"):
            return response.model_dump()
        elif hasattr(response, "dict"):
            return response.dict()
        else:
            logger.warning(f"Unable to serialize response of type {type(response)}")
            return {"status": "FAILED", "message": "Serialization error", "data": ""}
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}")
        return {"status": "FAILED", "message": f"Error: {str(e)}", "data": ""}

if __name__ == "__main__":
    logger.info("==== Starting RunPod serverless handler... ====")
    runpod.serverless.start({"handler": rp_handler})
