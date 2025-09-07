import logging
import asyncio
import threading
import time
import uuid
from typing import Optional

from .schemas import GenerateDescriptionRequest, JobDetails, JobResponse
from .shared import model_instance
from .model import ModelState

logger = logging.getLogger(__name__)

# Simple job simulation
# job_id -> {"status": "IN_PROGRESS|COMPLETED|ERROR", "result": None|JobDetails}
pending_jobs = {}

# Flag to track model loading status
model_loading_job_id = None

def _load_model_in_thread(job_id: str):
    """
    Background model loading process.
    Loads the model asynchronously and updates job status.
    """
    # Declarar variable global al principio de la función
    global model_loading_job_id
    
    # Wait a bit to simulate loading time
    time.sleep(3)
    
    try:
        # Actual model loading
        logger.info("======== Starting model loading in background thread ========")
        model_instance.load_model()
        logger.info("======== Model loading completed successfully ========")
        
        # Update job status to completed
        pending_jobs[job_id] = {
            "status": "COMPLETED",
            "result": JobDetails(
                status="IDLE",  # Ahora es IDLE porque el modelo ya está cargado
                message="Model warmup completed successfully",
                data=""
            )
        }
        
        # Asignar None al finalizar
        model_loading_job_id = None
        
    except Exception as e:
        error_msg = f"Model warmup failed: {str(e)}"
        logger.error(f"======== {error_msg} ========")
        
        # Update with error
        pending_jobs[job_id] = {
            "status": "ERROR",
            "result": JobDetails(
                status="ERROR",
                message=error_msg,
                data=""
            )
        }
        
        # Asignar None al finalizar
        model_loading_job_id = None


def _process_job_in_thread(job_id: str, text: str, prompt: Optional[str] = None):
    """
    Simulation of asynchronous background processing.
    In a real environment, this would run on a separate server.
    """
    # Wait a bit to simulate processing time
    time.sleep(5)
    
    try:
        # Use synchronous processing to avoid threading issues with async
        result = model_instance.generate_description(text, prompt)
        
        # Update job status
        pending_jobs[job_id] = {
            "status": "COMPLETED",
            "result": JobDetails(
                status="IDLE",
                message="Description generation completed successfully",
                data=result
            )
        }
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        error_msg = f"Inference failed: {str(e)}"
        logger.error(f"Job {job_id} failed: {error_msg}")
        
        # Update with error
        pending_jobs[job_id] = {
            "status": "ERROR",
            "result": JobDetails(
                status="ERROR",
                message=error_msg,
                data=""
            )
        }



def generate_description(request: GenerateDescriptionRequest) -> JobResponse:
    """
    Generate description using the preloaded adapter.
    Now returns a JobResponse with status for async simulation.
    
    Args:
        request: The description request containing text and optional prompt
        
    Returns:
        JobResponse: The job response with ID for tracking
    """
    # Generate unique ID for the job
    job_id = str(uuid.uuid4())
    
    # Check if model is ready using model's state
    if model_instance.state == ModelState.COLD:
        details = JobDetails(
            status="COLD",
            message=f"Model not ready. Current state: {model_instance.state.value}. Call warmup first.",
            data=""
        )
        return JobResponse(
            id=job_id,
            status="IN_QUEUE",
            details=details
        )

    if model_instance.state == ModelState.LOADING:
        details = JobDetails(
            status="LOADING",
            message=f"Model is currently loading...",
            data=""
        )
        return JobResponse(
            id=job_id,
            status="IN_PROGRESS",
            details=details
        )
    
    # Register job as in progress
    pending_jobs[job_id] = {
        "status": "IN_PROGRESS",
        "result": None
    }
    
    # Start background processing
    logger.info(f"======== Starting background processing for job {job_id} ========")
    thread = threading.Thread(
        target=_process_job_in_thread,
        args=(job_id, request.text, request.prompt)
    )
    thread.daemon = True
    thread.start()
    
    # Return immediate response with COMPLETED status but details.status=LOADING
    return JobResponse(
        id=job_id,
        status="COMPLETED",
        details=JobDetails(
            status="LOADING",
            message="Processing started. Check status with job ID.",
            data=""
        )
    )

def check_job_status(job_id: str) -> JobResponse:
    """
    Check the current status of a job.
    
    Args:
        job_id: ID of the job to check
        
    Returns:
        JobResponse with the current job status
    """
    # Check if job exists
    if job_id not in pending_jobs:
        # If job doesn't exist, return an error
        return JobResponse(
            id=job_id,
            status="COMPLETED",
            details=JobDetails(
                status="IDLE",
                message=f"Job ID {job_id} not found",
                data=""
            )
        )
    
    # Get job information
    job_info = pending_jobs[job_id]
    job_status = job_info["status"]
    job_result = job_info["result"]
    
    # Create response based on current status
    if job_status == "IN_PROGRESS":
        return JobResponse(
            id=job_id,
            status="COMPLETED",
            details=JobDetails(
                status="LOADING",
                message="Job is still processing",
                data=""
            )
        )
    elif job_status == "COMPLETED":
        return JobResponse(
            id=job_id,
            status="COMPLETED",
            details=job_result
        )
    else:  # ERROR
        return JobResponse(
            id=job_id,
            status="ERROR",
            details=job_result
        )


def warmup_model() -> JobResponse:
    """
    Trigger model loading (warmup) asynchronously.
    Returns immediately with status and starts background loading process.
    
    Returns:
        JobResponse: Job status with ID for tracking the loading process
    """
    global model_loading_job_id
    
    # If model is already idle, return completed status
    if model_instance.state == ModelState.IDLE:
        job_id = str(uuid.uuid4())
        return JobResponse(
            id=job_id,
            status="COMPLETED",
            details=JobDetails(
                status="IDLE",
                message="Model already loaded and ready",
                data=""
            )
        )
    
    # If there's already a loading job in progress, return its status
    if model_instance.state == ModelState.LOADING and model_loading_job_id is not None:
        # Get current loading job info
        if model_loading_job_id in pending_jobs:
            return JobResponse(
                id=model_loading_job_id,
                status="IN_PROGRESS",
                details=JobDetails(
                    status="LOADING",
                    message="Model is currently loading...",
                    data=""
                )
            )
    
    # Create a new job for model loading
    job_id = str(uuid.uuid4())
    model_loading_job_id = job_id
    
    # Register job as in progress
    pending_jobs[job_id] = {
        "status": "IN_PROGRESS",
        "result": None
    }
    
    logger.info(f"======== Starting model warmup in background thread... (job_id: {job_id}) ========")
    
    # Start loading in background thread
    thread = threading.Thread(
        target=_load_model_in_thread,
        args=(job_id,)
    )
    thread.daemon = True
    thread.start()
    
    # Return immediate response with COMPLETED status but details.status=LOADING
    return JobResponse(
        id=job_id,
        status="COMPLETED",
        details=JobDetails(
            status="LOADING",
            message="Model warmup started. Check status with job ID.",
            data=""
        )
    )