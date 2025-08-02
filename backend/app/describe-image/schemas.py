from pydantic import BaseModel, Field
from typing import Optional

# Real schemas from microservices
class DescribeImageRequest(BaseModel):
    """Schema for image description request (matches services/describe-image/schemas.py)"""
    image_url: str = Field(..., description="URL of the image to describe")
    model: Optional[str] = Field(None, description="Preferred model: 'openai', 'gemini', or 'qwen'")
    
class DescribeImageResponse(BaseModel):
    """Schema for image description response (matches services/describe-image/schemas.py)"""
    description: str = Field(..., description="Generated description of the image")