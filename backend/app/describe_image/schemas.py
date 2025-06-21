from pydantic import BaseModel

class DescribeImageRequest(BaseModel):
    """Schema for image description request."""
    image_url: str
    prompt: str
    
    
class DescribeImageResponse(BaseModel):
    """Schema for image description response."""
    description: str
