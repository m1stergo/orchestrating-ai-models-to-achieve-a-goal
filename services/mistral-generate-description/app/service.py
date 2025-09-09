import logging
import asyncio
import threading
import time
import uuid
from typing import Optional

from .schemas import GenerateDescriptionRequest, JobDetail, JobResponse
from .shared import model_instance
from .model import ModelState

logger = logging.getLogger(__name__)

# Simple job simulation
# job_id -> {"status": "IN_PROGRESS|COMPLETED|ERROR", "result": None|JobDetail}
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
            "result": JobDetail(
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
            "result": JobDetail(
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
        # Set model state to PROCESSING before starting generation
        model_instance._state = ModelState.PROCESSING
        # Use synchronous processing to avoid threading issues with async
        result = model_instance.generate_description(text, prompt)
        # Reset state to IDLE after processing
        model_instance._state = ModelState.IDLE
        
        # Update job status
        pending_jobs[job_id] = {
            "status": "COMPLETED",
            "result": JobDetail(
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
            "result": JobDetail(
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
        detail = JobDetail(
            status="COLD",
            message=f"Model not ready. Current state: {model_instance.state.value}. Call warmup first.",
            data=""
        )
        return JobResponse(
            id=job_id,
            status="IN_QUEUE",
            detail=detail
        )
        
    if model_instance.state == ModelState.WARMINGUP:
        detail = JobDetail(
            status="WARMINGUP",
            message=f"Model is warming up...",
            data=""
        )
        return JobResponse(
            id=job_id,
            status="IN_PROGRESS",
            detail=detail
        )
        
    if model_instance.state == ModelState.PROCESSING:
        detail = JobDetail(
            status="PROCESSING",
            message=f"Model is currently processing another request. Please try again later.",
            data=""
        )
        return JobResponse(
            id=job_id,
            status="IN_PROGRESS",
            detail=detail
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
    
    # Return response with IN_PROGRESS status and PROCESSING in detail.status
    return JobResponse(
        id=job_id,
        status="IN_PROGRESS",
        detail=JobDetail(
            status="PROCESSING",
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
            detail=JobDetail(
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
        # Si no hay resultado aún, necesitamos diferenciar entre warmup y processing
        if job_result is None:
            # Verificamos si este job es el job de warmup
            if job_id == model_loading_job_id:
                detail = JobDetail(
                    status="WARMINGUP",
                    message="Model is warming up...",
                    data=""
                )
            else:
                detail = JobDetail(
                    status="PROCESSING",
                    message="Job is still processing",
                    data=""
                )
        else:
            detail = job_result
            
        return JobResponse(
            id=job_id,
            status="IN_PROGRESS",
            detail=detail
        )
    elif job_status == "COMPLETED":
        if job_result is None:
            detail = JobDetail(
                status="IDLE",
                message="Job completed successfully",
                data=""
            )
        else:
            detail = job_result
            
        return JobResponse(
            id=job_id,
            status="COMPLETED",
            detail=detail
        )
    else:  # ERROR
        if job_result is None:
            detail = JobDetail(
                status="ERROR",
                message="Unknown error occurred",
                data=""
            )
        else:
            detail = job_result
            
        return JobResponse(
            id=job_id,
            status="ERROR",
            detail=detail
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
            detail=JobDetail(
                status="IDLE",
                message="Model already loaded and ready",
                data=""
            )
        )
    
    # If there's already a warmup job in progress, return its status
    if model_instance.state == ModelState.WARMINGUP and model_loading_job_id is not None:
        # Get current warmup job info
        if model_loading_job_id in pending_jobs:
            return JobResponse(
                id=model_loading_job_id,
                status="IN_PROGRESS",
                detail=JobDetail(
                    status="WARMINGUP",
                    message="Model is already warming up...",
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
    
    # Return response with IN_PROGRESS status and WARMINGUP in detail.status
    return JobResponse(
        id=job_id,
        status="IN_PROGRESS",
        detail=JobDetail(
            status="WARMINGUP",
            message="Model warmup started. Check status with job ID.",
            data=""
        )
    )