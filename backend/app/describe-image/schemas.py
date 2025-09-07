from typing import Optional, Any
from pydantic import BaseModel, Field

# API Request schemas
class DescribeImageRequest(BaseModel):
    image_url: str
    model: str = "openai"  # Default model
    prompt: Optional[str] = None
    
class WarmupRequest(BaseModel):
    model: str

class HealthCheckRequest(BaseModel):
    model: str

class StatusRequest(BaseModel):
    model: str
    job_id: Optional[str] = None

# Standardized Response schemas
class ResponseDetails(BaseModel):
    status: str = Field(..., description="Status of the operation: 'IDLE' or 'ERROR'")
    message: str = Field("", description="Optional message providing additional details")
    data: Any = Field("", description="The actual payload data, varies by endpoint")

class StandardResponse(BaseModel):
    status: str = Field(..., description="Overall status: 'COMPLETED', 'ERROR', 'IN_PROGRESS', 'IN_QUEUE', etc.")
    id: Optional[str] = Field(None, description="Optional ID for tracking async operations")
    details: ResponseDetails = Field(..., description="Detailed response information")