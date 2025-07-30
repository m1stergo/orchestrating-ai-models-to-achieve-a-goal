from pydantic import BaseModel, Field
from typing import Optional

class DescribeImageRequest(BaseModel):
    """Schema for image description request."""
    image_url: str = Field(..., description="URL of the image to describe")
    strategy: Optional[str] = Field(None, description="Preferred strategy: 'qwen' (local) or 'openai' (cloud). If not specified, uses the first available strategy.")
    
class DescribeImageResponse(BaseModel):
    """Schema for image description response."""
    description: str = Field(..., description="Generated description of the image")
    strategy_used: Optional[str] = Field(None, description="Strategy that was actually used to generate the description")
