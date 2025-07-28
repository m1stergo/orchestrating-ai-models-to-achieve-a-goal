from pydantic import BaseModel


class GenerateDescriptionRequest(BaseModel):
    """Schema for description generator request."""
    text: str
    prompt: str
    
    
class GenerateDescriptionResponse(BaseModel):
    """Schema for description generator response."""
    text: str
