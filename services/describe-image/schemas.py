from pydantic import BaseModel, Field
from typing import Optional

class DescribeImageRequest(BaseModel):
    """Schema for image description request."""
    image_url: str = Field(..., description="URL of the image to describe")
    model: Optional[str] = Field(None, description="Preferred model: 'openai', 'gemini', or 'qwen'")
    
class DescribeImageResponse(BaseModel):
    """Schema for image description response."""
    description: str = Field(..., description="Generated description of the image")
