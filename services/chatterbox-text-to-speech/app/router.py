"""API router module for AI microservice.

This module defines the API endpoints for the microservice, including
endpoints for running inference and checking job status. It uses the
RunPodSimulator to handle async job processing in a way that's compatible
with both local deployment and RunPod serverless.
"""

from fastapi import APIRouter
from typing import Dict, Any
from .common import JobResponse
import logging
# Import the specific handler from the service implementation
from .shared import handler
from .common import RunPodSimulator

# Create API router for endpoint definitions
router = APIRouter()
# Set up module logger
logger = logging.getLogger(__name__)

# Initialize the RunPod simulator with the service handler
pod = RunPodSimulator(handler)

@router.post("/run", response_model=JobResponse)
async def run(request: Dict[str, Any]):
    """Run inference with the AI model.
    
    This endpoint accepts input data and starts an asynchronous job to process
    the inference request. It returns a job ID that can be used to check the
    status of the job.
    
    Args:
        request: Dictionary containing input data for the model
        
    Returns:
        JobResponse: Object with job ID and status information
    """
    # Extract input data or use the whole request as input
    input_data = request.get('input', request)
    logger.info(f"Received run request with input data: {input_data}")
    # Process the request asynchronously using RunPodSimulator
    return pod.run(input_data)

@router.get("/status/{id}")
async def status(id: str):
    """Get the status of a job by ID.
    
    This endpoint allows checking the current status of a previously submitted job.
    It returns the job status and any output that may be available if the job has completed.
    
    Args:
        id: The job ID to check status for
        
    Returns:
        JobResponse: Object with job status and output information
    """
    logger.info(f"Received status request for job ID: {id}")
    return pod.status(id)
