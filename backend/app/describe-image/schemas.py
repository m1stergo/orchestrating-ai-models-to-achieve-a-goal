from typing import Optional
from pydantic import BaseModel, Field

# Real schemas from microservices
class DescribeImageRequest(BaseModel):
    image_url: str = Field(..., description="URL of the image to describe")
    model: str = Field(..., description="Preferred model: 'openai', 'gemini', or 'qwen'")
    prompt: Optional[str] = Field(None, description="Optional custom prompt for image description")
    
class DescribeImageResponse(BaseModel):
    description: str = Field(..., description="Generated description of the image")