from pydantic import BaseModel, Field
from typing import Optional

class DescribeImageRequest(BaseModel):
    """Schema for image description request."""
    action: Optional[str] = Field("inference", description="Action to perform: warmup, status, or inference")
    image_url: Optional[str] = Field(None, description="URL of the image to describe (required for inference)")
    prompt: Optional[str] = Field(None, description="Optional prompt to guide the description")
    
class DescribeImageResponse(BaseModel):
    status: Optional[str] = Field(None, description="Status of the operation")
    message: Optional[str] = Field(None, description="Optional message")
    description: Optional[str] = Field(None, description="Generated description of the image")
    state: Optional[str] = Field(None, description="Current model state")
    loading_time_seconds: Optional[float] = Field(None, description="Time taken for loading")
    elapsed_seconds: Optional[float] = Field(None, description="Elapsed time during loading")
    error: Optional[str] = Field(None, description="Error message if any")
