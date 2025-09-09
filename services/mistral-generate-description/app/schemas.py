from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


# Define job status as enum for consistency
class JobStatus(str, Enum):
    IN_QUEUE = "IN_QUEUE"      # Job is in queue but not processed yet
    IN_PROGRESS = "IN_PROGRESS"  # Job is being processed
    COMPLETED = "COMPLETED"    # Job is completed
    ERROR = "ERROR"            # Job encountered an error

class GenerateDescriptionRequest(BaseModel):
    """Schema for description generator request."""
    text: str = Field(..., description="Product information to generate description from")
    prompt: Optional[str] = Field(None, description="Optional custom prompt to guide the generation")
    
class JobDetail(BaseModel):
    status: Optional[str] = Field(None, description="Status of the operation")
    message: Optional[str] = Field(None, description="Optional message")
    data: Optional[str] = Field(None, description="Generated description")

# RunPod-like schemas
class JobRequest(BaseModel):
    """RunPod-compatible job request."""
    input: Dict[str, Any] = Field(..., description="Input data for the job")

class JobResponse(BaseModel):
    """RunPod-compatible job response."""
    id: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job status")
    workerId: str = Field(default="mistral-worker", description="Worker ID")
    detail: Optional[JobDetail] = None
