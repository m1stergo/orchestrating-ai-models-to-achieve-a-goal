from typing import Optional
from pydantic import BaseModel

# Real schemas from microservices
class DescribeImageRequest(BaseModel):
    image_url: str
    model: str = "openai"  # Default model
    prompt: Optional[str] = None
    
class DescribeImageResponse(BaseModel):
    description: str

class WarmupRequest(BaseModel):
    model: str

class HealthCheckRequest(BaseModel):
    model: str