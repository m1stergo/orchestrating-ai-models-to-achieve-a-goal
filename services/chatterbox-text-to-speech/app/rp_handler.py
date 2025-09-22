"""RunPod serverless handler module.

This module provides integration with RunPod's serverless platform for AI model inference.
It defines a handler function that processes RunPod events and delegates the
actual inference work to the service's handler implementation.

This allows the service to be deployed as a serverless function on RunPod with
minimal code changes, while maintaining compatibility with local development.
"""

import logging
import runpod
from typing import Any, Dict
# Import the specific handler implementation from the service
from .shared import handler
from .common import InferenceStatus, InferenceResponse

# Configure basic logging for RunPod environment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rp_handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process RunPod serverless events and return responses.
    
    This is the main entry point for RunPod's serverless platform. It receives
    events from RunPod, processes them using the service's handler implementation,
    and returns a response in the format expected by RunPod.
    
    Args:
        event: The RunPod event containing input data and metadata
        
    Returns:
        Dict[str, Any]: Response data in RunPod's expected format
        
    Note:
        The handler supports two main actions:
        - "inference": Run model inference with the provided input data
        - "warmup": Load the model into memory (usually called on pod startup)
    """
    # Extract input data from the event
    input_data = event.get("input", {})
    logger.info(f"==== Received RunPod event with input: {input_data} ====")
    
    # Determine the action to perform (default to inference)
    action = input_data.get("action", "inference")
    
    try:
        # Check if the model is already busy processing another request
        if (handler.is_busy()):
            return InferenceResponse(
                status=handler.status, 
                message="Model is currently processing another request. Please try again later."
            )
        
        # Process based on the requested action
        if action == "inference":
            # Run inference using the service handler
            response = handler.infer(input_data)
        elif action == "warmup":
            # Load the model (typically called on pod startup)
            response = handler.load_model()
        else:
            # Handle unknown action type
            response = InferenceResponse(
                status=InferenceStatus.FAILED, 
                message="Invalid action"
            )
        
        # Convert the response to a dictionary for RunPod
        if hasattr(response, "model_dump"):  # Pydantic v2
            return response.model_dump()
        elif hasattr(response, "dict"):      # Pydantic v1
            return response.dict()
        else:
            # Handle case where response is not a Pydantic model
            logger.warning(f"Unable to serialize response of type {type(response)}")
            return {"status": "FAILED", "message": "Serialization error", "data": ""}
    
    except Exception as e:
        # Handle any unexpected errors
        logger.error(f"Error in handler: {str(e)}")
        return {"status": "FAILED", "message": f"Error: {str(e)}", "data": ""}

if __name__ == "__main__":
    logger.info("==== Starting RunPod serverless handler... ====")
    runpod.serverless.start({"handler": rp_handler})
