from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum
from abc import ABC, abstractmethod
import time
import threading
import uuid
import logging


logger = logging.getLogger(__name__)

# Define job status as enum for consistency
class JobStatus(str, Enum):
    IN_QUEUE = "IN_QUEUE"      # Job is in queue but not processed yet
    IN_PROGRESS = "IN_PROGRESS"  # Job is being processed
    COMPLETED = "COMPLETED"    # Job is completed
    ERROR = "ERROR"            # Job encountered an error
    
class JobDetail(BaseModel):
    status: Optional[str] = Field(None, description="Status of the operation")
    message: Optional[str] = Field(None, description="Optional message")
    data: Optional[str] = Field(None, description="Generated description of the image")

# RunPod-like schemas
class JobRequest(BaseModel):
    """RunPod-compatible job request."""
    input: Dict[str, Any] = Field(..., description="Input data for the job")

class JobResponse(BaseModel):
    """RunPod-compatible job response."""
    id: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job status")
    workerId: str = Field(default="qwen-worker", description="Worker ID")
    detail: Optional[JobDetail] = None

class InferenceRequest(BaseModel):
    """Modelo genérico para solicitudes de inferencia.
    
    Solo 'action' es obligatorio, todos los demás campos son dinámicos.
    """
    # Único campo obligatorio para identificar el tipo de acción
    action: str
    
    # Permitir cualquier campo adicional como dict[str, Any]
    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            return None

class ModelState(Enum):
    COLD = "COLD" 
    WARMINGUP = "WARMINGUP"
    PROCESSING = "PROCESSING"
    IDLE = "IDLE"
    ERROR = "ERROR"


class InferenceModel(ABC):
    """Abstract base class for inference models.
    All model implementations must inherit from this class and implement the required methods.
    """
    def __init__(self):
        self._model = None
        self._state = ModelState.COLD
        self._loading_start_time = None
        self._error_message = None
        self.model_name = None
    
    @abstractmethod
    def load_model(self):
        """Load the model. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def inference(self, request_data: Dict[str, Any]):
        """Run inference with the model. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def is_loaded(self):
        """Check if model is loaded."""
        pass
    
    @property
    def state(self) -> ModelState:
        """Get current model state."""
        return self._state
    
    @property
    def error_message(self) -> str:
        """Get error message if state is ERROR."""
        return self._error_message
    
    @property
    def loading_start_time(self) -> float:
        """Get loading start time."""
        return self._loading_start_time

class InferenceHandler:
    """ Class that handles inference requests. """
    def __init__(self, model: InferenceModel, model_name: str):
        self.model_name = model_name
        self.model = model
        self.model_loaded = False
        self.pending_jobs = {}
        self.model_loading_job_id = None

    def run_job(self, request_data: Dict[str, Any]):
        """
        RunPod-compatible endpoint that executes jobs and returns RunPod format.
        
        Args:
            request_data: Dict[str, Any]: Dictionary containing request parameters
        """
        try:
            action = request_data.get('action')
            
            logger.info(f"======== Inference handler called with action: {action} ========")
            
            if action == "inference":
                return self.inference(request_data)
                
            elif action == "warmup":
                return self.warmup()
                
            else:
                return JobResponse(
                    id="none",
                    status="ERROR",
                    detail=JobDetail(
                        status="ERROR",
                        message=f"Unknown action: {action}. Valid actions: warmup, inference",
                        data=""
                    )
                )
                
        except Exception as e:
            logger.error(f"Job execution failed: {str(e)}")
            
            return JobResponse(
                id="none",
                status="ERROR",
                detail=JobDetail(
                    status="ERROR",
                    message=str(e),
                    data=""
                )
            )
    
    def _load_model_in_thread(self, job_id: str):
        """
        Background model loading process.
        Loads the model asynchronously and updates job status.
        """
        # Wait a bit to simulate loading time
        time.sleep(3)
        
        try:
            # Set model state to WARMINGUP
            self.model._state = ModelState.WARMINGUP
            logger.info("======== Starting model loading in background thread ========")
            self.model.load_model()
            logger.info("======== Model loading completed successfully ========")
            
            # Update job status to completed
            self.pending_jobs[job_id] = {
                "status": "COMPLETED",
                "result": JobDetail(
                    status="IDLE",
                    message="Model warmup completed successfully",
                    data=""
                )
            }
            
            self.model_loading_job_id = None
            
        except Exception as e:
            error_msg = f"Model warmup failed: {str(e)}"
            logger.error(f"======== {error_msg} ========")
            
            # Update with error
            self.pending_jobs[job_id] = {
                "status": "ERROR",
                "result": JobDetail(
                    status="ERROR",
                    message=error_msg,
                    data=""
                )
            }
            
            self.model_loading_job_id = None

    def _process_job_in_thread(self, job_id: str, request_data: Dict[str, Any]):
        """
        Simulation of asynchronous background processing.
        In a real environment, this would run on a separate server.
        """
        # Wait a bit to simulate processing time
        time.sleep(5)
        
        try:
            # Set model state to PROCESSING before starting inference
            self.model._state = ModelState.PROCESSING
            
            logger.info(f"======== Processing job {job_id} with request_data: {request_data} ========")
            
            result = self.model.inference(request_data)
            # Reset state to IDLE after processing
            self.model._state = ModelState.IDLE
            
            # Update job status
            self.pending_jobs[job_id] = {
                "status": "COMPLETED",
                "result": JobDetail(
                    status="IDLE",
                    message="Inference completed successfully",
                    data=result
                )
            }
            logger.info(f"======== Job {job_id} completed successfully ========")
            
        except Exception as e:
            error_msg = f"Inference failed: {str(e)}"
            logger.error(f"======== Job {job_id} failed: {error_msg} ========")
            
            # Update with error
            self.pending_jobs[job_id] = {
                "status": "ERROR",
                "result": JobDetail(
                    status="ERROR",
                    message=error_msg,
                    data=""
                )
            }

    def check_job_status(self, job_id: str) -> JobResponse:
        """
        Check the current status of a job.
        
        Args:
            job_id: ID of the job to check
            
        Returns:
            JobResponse with the current job status
        """
        # Check if job exists
        if job_id not in self.pending_jobs:
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
        job_info = self.pending_jobs[job_id]
        job_status = job_info["status"]
        job_result = job_info["result"]
        
        # Create response based on current status
        if job_status == "IN_PROGRESS":
            # Si no hay resultado aún, necesitamos diferenciar entre warmup y processing
            if job_result is None:
                # Verificamos si este job es el job de warmup
                if job_id == self.model_loading_job_id:
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

    def inference(self, request_data: Dict[str, Any]) -> JobResponse:
        job_id = str(uuid.uuid4())
        
        if self.model.state == ModelState.COLD:
            detail = JobDetail(
                status="COLD",
                message=f"Model not ready. Current state: {self.model.state.value}. Call warmup first.",
                data=""
            )
            return JobResponse(
                id=job_id,
                status="IN_QUEUE",
                detail=detail
            )
            
        if self.model.state == ModelState.WARMINGUP:
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
            
        if self.model.state == ModelState.PROCESSING:
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
        self.pending_jobs[job_id] = {
            "status": "IN_PROGRESS",
            "result": None
        }
        
        # Start background processing
        logger.info(f"======== Starting background processing for job {job_id} ========")
        thread = threading.Thread(
            target=self._process_job_in_thread,
            args=(job_id, request_data)
        )
        thread.daemon = True
        thread.start()
        
        return JobResponse(
            id=job_id,
            status="IN_PROGRESS",
            detail=JobDetail(
                status="PROCESSING",
                message="Processing started. Check status with job ID.",
                data=""
            )
        )

    def warmup(self) -> JobResponse:
        """
        Trigger model loading (warmup) asynchronously.
        Returns immediately with status and starts background loading process.
        
        Returns:
            JobResponse: Job status with ID for tracking the loading process
        """
        
        if self.model.state == ModelState.IDLE:
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
        
        if self.model.state == ModelState.PROCESSING:
            job_id = str(uuid.uuid4())
            return JobResponse(
                id=job_id,
                status="IN_QUEUE",
                detail=JobDetail(
                    status="PROCESSING",
                    message="Model is currently processing another request. Warmup will be queued.",
                    data=""
                )
            )
            
        if self.model.state == ModelState.WARMINGUP and self.model_loading_job_id is not None:
            return JobResponse(
                id=self.model_loading_job_id,
                status="IN_PROGRESS",
                detail=JobDetail(
                    status="WARMINGUP",
                    message="Model is warming up...",
                    data=""
                )
            )
        
        # Create a new job for model loading
        job_id = str(uuid.uuid4())
        self.model_loading_job_id = job_id
        
        # Register job as in progress
        self.pending_jobs[job_id] = {
            "status": "IN_PROGRESS",
            "result": None
        }
        
        logger.info(f"======== Starting model warmup in background thread... (job_id: {job_id}) ========")
        
        # Start loading in background thread
        thread = threading.Thread(
            target=self._load_model_in_thread,
            args=(job_id,)
        )
        thread.daemon = True
        thread.start()
        
        return JobResponse(
            id=job_id,
            status="IN_PROGRESS",
            detail=JobDetail(
                status="WARMINGUP",
                message="Model warmup started. Check status with job ID.",
                data=""
            )
        )
