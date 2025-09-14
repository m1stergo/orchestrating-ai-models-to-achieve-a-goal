from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum
from abc import ABC, abstractmethod
import time
import threading
import uuid
import logging
import torch
import os
from .config import settings

logger = logging.getLogger(__name__)

# Define status enums for consistency
class JobStatus(str, Enum):
    IN_QUEUE = "IN_QUEUE"      # Job is in queue but not processed yet
    IN_PROGRESS = "IN_PROGRESS"  # Job is being processed
    COMPLETED = "COMPLETED"    # Job is completed

class InferenceStatus(str, Enum):
    COLD = "COLD" 
    WARMINGUP = "WARMINGUP"
    PROCESSING = "PROCESSING"
    IDLE = "IDLE"
    FAILED = "FAILED"

# RunPod-like schemas
class JobRequest(BaseModel):
    """RunPod-compatible job request."""
    input: Dict[str, Any] = Field(..., description="Input data for the job")

class InferenceResponse(BaseModel):
    status: InferenceStatus = Field(..., description="Inference status")
    message: Optional[str] = Field(None, description="Status message")
    data: Optional[str] = Field(None, description="Inference result")

class JobResponse(BaseModel):
    """RunPod-compatible job response."""
    id: str = Field(..., description="Job ID")
    status: JobStatus = Field(..., description="Job status")
    output: Optional[InferenceResponse] = None

class InferenceRequest(BaseModel):
    action: str
    
    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            return None

class InferenceHandler(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.status = InferenceStatus.COLD
        self.loading_start_time = None
        self.error_message = None

    def require_gpu(self) -> bool:
        device_available = torch.cuda.is_available()
        logger.info(f"==== CUDA available: {device_available} ====")
        
        if not device_available:
            error_msg = "GPU is required for this service. No CUDA-compatible GPU detected. Terminating process."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def load_model(self) -> InferenceResponse:
        self.require_gpu()
        
        if self.is_loaded():
            self.status = InferenceStatus.IDLE
            logger.info("==== Model is ready to use. ====")
            return InferenceResponse(
                status=InferenceStatus.IDLE,
                message="Model is ready to use.",
                data=""
            )

        self.status = InferenceStatus.WARMINGUP
        self.loading_start_time = time.time()
        self.error_message = None
        
        # Set HuggingFace cache directory if specified
        if settings.HUGGINGFACE_CACHE_DIR:
            cache_dir = settings.HUGGINGFACE_CACHE_DIR
            os.environ['TRANSFORMERS_CACHE'] = cache_dir
            os.environ['HF_HOME'] = cache_dir
            logger.info(f"==== Using custom HuggingFace cache directory: {cache_dir} ====")
        else:
            logger.info("==== Using default HuggingFace cache directory ====")

        return self._do_load_model()
    
    @abstractmethod
    def _do_load_model(self) -> InferenceResponse:
        pass
    
    @abstractmethod
    def infer(self, request_data: Dict[str, Any]) -> InferenceResponse:
        pass
    
    @abstractmethod
    def is_loaded(self) -> bool:
        pass

    def getInferenceStatus(self) -> InferenceResponse:
        # Usar self.status directamente en lugar de self.model.status
        if self.status == InferenceStatus.FAILED:
            return InferenceResponse(
                status=InferenceStatus.FAILED,
                message=f"Model is in FAILED status: {self.error_message}",
                data=""
            )
        
        if self.status == InferenceStatus.COLD:
            return InferenceResponse(
                status=InferenceStatus.COLD,
                message=f"Model not ready. Current status: {self.status}. Call warmup first.",
                data=""
            )
            
        if self.status == InferenceStatus.WARMINGUP:
            return InferenceResponse(
                status=InferenceStatus.WARMINGUP,
                message=f"Model is warming up...",
                data=""
            )
            
        if self.status == InferenceStatus.PROCESSING:
            return InferenceResponse(
                status=InferenceStatus.PROCESSING,
                message=f"Model is currently processing another request. Please try again later.",
                data=""
            )

        return InferenceResponse(
            status=InferenceStatus.IDLE,
            message=f"Model is ready to use.",
            data=""
        )

class RunPodSimulator:
    """ Class that handles inference requests. """
    def __init__(self, model: InferenceHandler):
        self.model = model
        self.job = {
            "status": JobStatus.IN_QUEUE,
            "output": None
        }
        self.busy = False

    def run(self, request_data: Dict[str, Any]) -> JobResponse:
        """
        RunPod-compatible endpoint that executes jobs and returns RunPod format.
        
        Args:
            request_data: Dict[str, Any]: Dictionary containing request parameters
        """

        if self.busy:
            return JobResponse(
                id=self.job['id'],
                status=self.job['status'],
                output=self.job['output']
            )

        job_id = str(uuid.uuid4())
        
        try:
            logger.info(f"==== Processing job {job_id} with request_data: {request_data} ====")

            action = request_data.get('action')

            thread = threading.Thread(
                target=self._process_request,
                args=(job_id, action, request_data)
            )
            thread.daemon = True
            thread.start()
                
            return JobResponse(
                id=job_id,
                status=JobStatus.IN_PROGRESS
            )
                
        except Exception as e:
            logger.error(f"Job execution failed: {str(e)}")
            self.busy = False
            
            return JobResponse(
                id=job_id,
                status=JobStatus.COMPLETED,
                output=InferenceResponse(
                    status=InferenceStatus.FAILED,
                    message=str(e),
                    data=""
                )
            )

    def _process_request(self, job_id: str, action: str, request_data: Dict[str, Any]):
        try:
            self.busy = True
            self.job['status'] = JobStatus.IN_PROGRESS
            self.job['output'] = InferenceResponse(
                status=InferenceStatus.WARMINGUP if action == "warmup" else InferenceStatus.PROCESSING,
                message="Warming up..." if action == "warmup" else "Processing...",
                data=""
            )
            
            output = self.model.load_model() if action == "warmup" else self.model.infer(request_data)
            
            self.job['status'] = JobStatus.COMPLETED
            self.job['output'] = output
            self.busy = False

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            self.job['status'] = JobStatus.COMPLETED
            self.job['output'] = InferenceResponse(
                status=InferenceStatus.FAILED,
                message=f"Error: {str(e)}",
                data=""
            )
            self.busy = False    
    
    def status(self, job_id: str) -> JobResponse:
        """
        Check the current status of a job.
        
        Args:
            job_id: ID of the job to check
            
        Returns:
            JobResponse with the current job status
        """
        return JobResponse(
            id=job_id,
            status=self.job['status'],
            output=self.job['output']
        )
