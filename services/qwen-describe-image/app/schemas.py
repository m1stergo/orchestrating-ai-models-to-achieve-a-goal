from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Original schemas for direct calls
class DescribeImageRequest(BaseModel):
    """Schema for image description request."""
    image_url: Optional[str] = Field(None, description="URL of the image to describe (required for inference)")
    prompt: Optional[str] = Field(None, description="Optional prompt to guide the description")
    
class DescribeImageResponse(BaseModel):
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
    delayTime: int = Field(..., description="Delay time in milliseconds")
    executionTime: Optional[int] = Field(None, description="Execution time in milliseconds")
    workerId: str = Field(..., description="Worker ID")
    output: Optional[Dict[str, Any]] = Field(None, description="Job output")
