"""Common components for AI microservices.

This module provides shared classes and utilities used across all AI microservices,
including:
- Status enums for job and inference tracking
- Pydantic models for request/response data structures
- Base handler class for AI model inference
- RunPod job simulation for asynchronous processing

These components allow services to be run both locally and on RunPod's serverless
platform with minimal code changes.
"""

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
import pathlib
from .config import settings

# Configure module logger
logger = logging.getLogger(__name__)

# Status enums for tracking job and inference states
class JobStatus(str, Enum):
    """Status values for asynchronous jobs.
    
    This enum defines the possible states of an asynchronous job in the system.
    
    Attributes:
        IN_QUEUE: Job is waiting to be processed
        IN_PROGRESS: Job is currently being processed
        COMPLETED: Job has finished processing (successfully or with errors)
    """
    IN_QUEUE = "IN_QUEUE"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class InferenceStatus(str, Enum):
    """Status values for AI model inference.
    
    This enum defines the possible states of an AI model during the inference process.
    
    Attributes:
        COLD: Model is not loaded yet
        WARMINGUP: Model is being loaded into memory
        IN_PROGRESS: Model is processing an inference request
        COMPLETED: Model has completed the inference request successfully
        FAILED: Model encountered an error during inference
        IN_QUEUE: Inference request is waiting to be processed
    """
    COLD = "COLD"
    WARMINGUP = "WARMINGUP"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    IN_QUEUE = "IN_QUEUE"

class JobRequest(BaseModel):
    """RunPod-compatible job request model.
    
    This model represents an incoming job request in the format expected by RunPod.
    
    Attributes:
        input: Dictionary containing input data and parameters for the job
    """
    input: Dict[str, Any] = Field(..., description="Input data for the job")

class InferenceResponse(BaseModel):
    """Response model for AI model inference.
    
    This model represents the response from an inference operation,
    including status, message, and any generated data.
    
    Attributes:
        status: Current status of the inference operation
        message: Optional message providing details about the operation
        data: Optional data produced by the inference operation
    """
    status: InferenceStatus = Field(..., description="Status of the inference operation")
    message: Optional[str] = Field(None, description="Optional message with details")
    data: Optional[str] = Field(None, description="Data produced by inference")

class JobResponse(BaseModel):
    """Response model for asynchronous jobs.
    
    This model represents the response for an asynchronous job,
    including ID, status, and output if available.
    
    Attributes:
        id: Unique identifier for the job
        status: Current status of the job
        output: Optional inference response if the job is completed
    """
    id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    output: Optional[InferenceResponse] = Field(None, description="Inference output when complete")

class InferenceRequest(BaseModel):
    """Request model for AI model inference.
    
    This model represents an incoming request for inference, with flexible
    fields to accommodate different model requirements.
    
    Attributes:
        action: The action to perform (e.g., "inference", "warmup")
    """
    action: str = Field(..., description="Action to perform (inference, warmup)")
    
    class Config:
        """Pydantic configuration for InferenceRequest."""
        # Allow extra fields beyond those explicitly defined
        extra = "allow"
        # Allow arbitrary types in the model
        arbitrary_types_allowed = True
        
    def __getattr__(self, name):
        """Dynamic attribute access for flexible field handling.
        
        Args:
            name: Name of the attribute to access
            
        Returns:
            The attribute value or None if not found
        """
        try:
            return self.__dict__[name]
        except KeyError:
            return None

class InferenceHandler(ABC):
    """Abstract base class for AI model inference handlers.
    
    This class defines the interface and common functionality for all AI model handlers.
    Each specific model implementation should extend this class and implement the
    required abstract methods.
    
    Attributes:
        model_name: Name of the AI model
        model: The actual model instance (when loaded)
        status: Current status of the model
        loading_start_time: Timestamp when model loading started
        error_message: Error message if something went wrong
    """
    def __init__(self, model_name: str):
        """Initialize the inference handler.
        
        Args:
            model_name: Name of the AI model to use
        """
        self.model_name = model_name
        self.model = None
        self.status = InferenceStatus.COLD
        self.loading_start_time = None
        self.error_message = None

    def require_gpu(self) -> bool:
        """Verify that a GPU is available for the model.
        
        This method checks if CUDA is available and raises an exception if not,
        as most AI models require GPU acceleration.
        
        Returns:
            bool: True if a GPU is available (function will raise an exception otherwise)
            
        Raises:
            RuntimeError: If no CUDA-compatible GPU is detected
        """
        device_available = torch.cuda.is_available()
        logger.info(f"==== CUDA available: {device_available} ====")
        if not device_available:
            error_msg = "GPU is required for this service. No CUDA-compatible GPU detected. Terminating process."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        return True

    def load_model(self) -> InferenceResponse:
        """Load the AI model into memory.
        
        This method handles the common steps for model loading, including GPU verification,
        environment setup, and status tracking. The actual model loading is delegated to
        the _do_load_model method that must be implemented by subclasses.
        
        Returns:
            InferenceResponse: Response with the status of the model loading operation
        """
        # Verify GPU availability
        self.require_gpu()
        
        # Log environment configuration
        logger.info(f"==== Using HF cache: {settings.HUGGINGFACE_CACHE_DIR} ====")
        logger.info(f"==== Using TMPDIR: {settings.TMPDIR} ====")
        logger.info(f"==== Models dir: {settings.MODELS_DIR} ====")
        logger.info(f"==== Offload dir: /runpod-volume/offload ====")

        # Check if model is already loaded
        if self.is_loaded():
            self.status = InferenceStatus.COMPLETED
            logger.info("==== Model is ready to use. ====")
            return InferenceResponse(status=InferenceStatus.COMPLETED, message="Model is ready to use.")

        # Prepare for model loading
        self.status = InferenceStatus.WARMINGUP
        self.loading_start_time = time.time()
        self.error_message = None
        
        # Configure HuggingFace cache directory
        if settings.HUGGINGFACE_CACHE_DIR:
            cache_dir = settings.HUGGINGFACE_CACHE_DIR
            os.environ['TRANSFORMERS_CACHE'] = cache_dir
            os.environ['HF_HOME'] = cache_dir
            os.environ['HF_HUB_CACHE'] = cache_dir
            logger.info(f"==== Using custom HuggingFace cache directory: {cache_dir} ====")
        else:
            logger.info("==== Using default HuggingFace cache directory ====")

        # Delegate to the specific implementation
        return self._do_load_model()

    @abstractmethod
    def _do_load_model(self) -> InferenceResponse:
        """Load the specific AI model into memory.
        
        This abstract method must be implemented by subclasses to handle
        the actual loading of the AI model.
        
        Returns:
            InferenceResponse: Response with status of the model loading operation
        """
        pass
    
    @abstractmethod
    def infer(self, request_data: Dict[str, Any]) -> InferenceResponse:
        """Run inference with the AI model.
        
        This abstract method must be implemented by subclasses to perform
        inference using the loaded model.
        
        Args:
            request_data: Input data for the inference
            
        Returns:
            InferenceResponse: Response containing inference results
        """
        pass
    
    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready for inference.
        
        This abstract method must be implemented by subclasses to determine
        if the model is fully loaded and ready to use.
        
        Returns:
            bool: True if the model is loaded, False otherwise
        """
        pass

    def getInferenceStatus(self) -> InferenceResponse:
        """Get the current status of the inference handler.
        
        This method provides a standardized way to check the current status
        of the model and handler.
        
        Returns:
            InferenceResponse: Response with current status information
        """
        if self.status == InferenceStatus.FAILED:
            return InferenceResponse(
                status=InferenceStatus.FAILED, 
                message=f"Model is in FAILED status: {self.error_message}"
            )
        if self.status == InferenceStatus.COLD:
            return InferenceResponse(
                status=InferenceStatus.COLD, 
                message=f"Model not ready. Current status: {self.status}. Call warmup first."
            )
        if self.status == InferenceStatus.WARMINGUP:
            return InferenceResponse(
                status=InferenceStatus.WARMINGUP, 
                message="Model is warming up..."
            )
        if self.status == InferenceStatus.IN_PROGRESS:
            return InferenceResponse(
                status=InferenceStatus.IN_PROGRESS, 
                message="Model is currently processing another request. Please try again later."
            )
        return InferenceResponse(
            status=InferenceStatus.COMPLETED, 
            message="Model is ready to use."
        )
        
    def is_busy(self) -> bool:
        """Check if the model is currently busy.
        
        This method determines if the model is currently processing a request
        or warming up, and thus unable to handle new requests.
        
        Returns:
            bool: True if the model is busy, False otherwise
        """
        logger.debug(f"Model status: {self.status}")
        return self.status == InferenceStatus.IN_PROGRESS or self.status == InferenceStatus.WARMINGUP

class RunPodSimulator:
    """Simulates RunPod's serverless job handling for local development.
    
    This class provides a way to run asynchronous AI inference jobs in a manner
    compatible with both local development and RunPod's serverless platform.
    It handles job creation, tracking, and status reporting.
    
    Attributes:
        model: The inference handler to use for processing requests
        job: Dictionary with current job information
        busy: Flag indicating if a job is currently being processed
    """
    def __init__(self, model: InferenceHandler):
        """Initialize the RunPod simulator.
        
        Args:
            model: The inference handler to use for processing requests
        """
        self.model = model
        self.job = {"status": JobStatus.IN_QUEUE, "output": None}
        self.busy = False

    def run(self, request_data: Dict[str, Any]) -> JobResponse:
        """Run an inference job asynchronously.
        
        This method creates a new job for the inference request and starts processing
        it in a background thread to simulate asynchronous processing.
        
        Args:
            request_data: Input data for the inference request
            
        Returns:
            JobResponse: Initial response with job ID and status
        """
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        
        try:
            # Check if the model is already busy
            if self.model.is_busy():
                logger.warning("Model is busy processing another request")
                return JobResponse(
                    id=self.job.get('id', 'busy'), 
                    status=self.job['status'], 
                    output=self.job['output']
                )
                
            logger.info(f"==== Processing job {job_id} with request_data: {request_data} ====")
            
            # Get action from request data (defaults to "inference" if not specified)
            action = request_data.get('action')
            
            # Start processing in a background thread
            thread = threading.Thread(
                target=self._process_request, 
                args=(job_id, action, request_data)
            )
            thread.daemon = True
            thread.start()
            
            # Return initial response immediately
            return JobResponse(id=job_id, status=JobStatus.IN_PROGRESS)
            
        except Exception as e:
            logger.error(f"Job execution failed: {str(e)}")
            self.busy = False
            return JobResponse(
                id=job_id, 
                status=JobStatus.COMPLETED, 
                output=InferenceResponse(status=InferenceStatus.FAILED, message=str(e))
            )

    def _process_request(self, job_id: str, action: str, request_data: Dict[str, Any]):
        """Process a request in a background thread.
        
        This method handles the actual processing of the request in a background thread,
        updating the job status and output as it progresses.
        
        Args:
            job_id: Unique identifier for the job
            action: Action to perform ("inference" or "warmup")
            request_data: Input data for the request
        """
        try:
            # Mark the job as in progress
            self.busy = True
            self.job['id'] = job_id
            self.job['status'] = JobStatus.IN_PROGRESS
            
            # Set initial status based on action
            initial_status = InferenceStatus.WARMINGUP if action == "warmup" else InferenceStatus.IN_PROGRESS
            initial_message = "Warming up..." if action == "warmup" else "Processing..."
            self.job['output'] = InferenceResponse(status=initial_status, message=initial_message)
            
            # Process the request based on action
            output = self.model.load_model() if action == "warmup" else self.model.infer(request_data)
            
            # Update job with final status and output
            self.job['status'] = JobStatus.COMPLETED
            self.job['output'] = output
            self.busy = False
            
        except Exception as e:
            # Handle any errors during processing
            logger.error(f"Error processing job {job_id}: {str(e)}")
            self.job['status'] = JobStatus.COMPLETED
            self.job['output'] = InferenceResponse(
                status=InferenceStatus.FAILED, 
                message=f"Error: {str(e)}"
            )
            self.busy = False

    def status(self, job_id: str) -> JobResponse:
        """Get the current status of a job.
        
        Args:
            job_id: Unique identifier for the job
            
        Returns:
            JobResponse: Current status and output of the job
        """
        return JobResponse(
            id=job_id, 
            status=self.job['status'], 
            output=self.job['output']
        )
