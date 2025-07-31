from pydantic import BaseModel, Field
from typing import Optional, Dict
from enum import Enum

class ServiceStatus(str, Enum):
    """Service health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class ServiceType(str, Enum):
    """Service type"""
    EXTERNAL = "external"
    INTERNAL = "internal"

# Real schemas from microservices
class DescribeImageRequest(BaseModel):
    """Schema for image description request (matches services/describe-image/schemas.py)"""
    image_url: str = Field(..., description="URL of the image to describe")
    strategy: Optional[str] = Field(None, description="Preferred strategy: 'openai', 'gemini', or 'qwen'")
    
class DescribeImageResponse(BaseModel):
    """Schema for image description response (matches services/describe-image/schemas.py)"""
    description: str = Field(..., description="Generated description of the image")
    strategy_used: Optional[str] = Field(None, description="Strategy that was actually used to generate the description")

class GenerateDescriptionRequest(BaseModel):
    """Schema for description generator request (matches services/generate-description/schemas.py)"""
    text: str = Field(..., description="Product information to generate description from")
    strategy: Optional[str] = Field(None, description="Preferred strategy: 'openai', 'gemini', or 'mistral'")
    
class GenerateDescriptionResponse(BaseModel):
    """Schema for description generator response (matches services/generate-description/schemas.py)"""
    text: str = Field(..., description="Generated product description")
    strategy_used: Optional[str] = Field(None, description="Strategy that was actually used to generate the description")

class ServiceHealthInfo(BaseModel):
    """Health information for a service"""
    status: ServiceStatus = Field(..., description="Service health status")
    type: ServiceType = Field(..., description="Service type (internal or external)")
    url: Optional[str] = Field(None, description="Service URL if external")
    error: Optional[str] = Field(None, description="Error message if unhealthy")
    note: Optional[str] = Field(None, description="Additional notes")

class ServicesHealthResponse(BaseModel):
    """Response model for services health check"""
    services: Dict[str, ServiceHealthInfo] = Field(..., description="Health status of all services")

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str = Field(..., description="Error message")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    service: Optional[str] = Field(None, description="Service that generated the error")
