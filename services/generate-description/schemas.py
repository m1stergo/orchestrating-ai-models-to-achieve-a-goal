from pydantic import BaseModel, Field
from typing import Optional


class GenerateDescriptionRequest(BaseModel):
    """Schema for description generator request."""
    text: str = Field(..., description="Product information to generate description from")
    model: Optional[str] = Field(None, description="Preferred model: 'openai', 'gemini', or 'mistral'")
    

class GenerateDescriptionResponse(BaseModel):
    """Schema for description generator response."""
    text: str = Field(..., description="Generated product description")
