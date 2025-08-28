from pydantic import BaseModel, Field
from typing import Optional


class GenerateDescriptionRequest(BaseModel):
    """Schema for description generator request."""
    text: str = Field(..., description="Product information to generate description from")
    prompt: Optional[str] = Field(None, description="Optional custom prompt to guide the generation")
    

class GenerateDescriptionResponse(BaseModel):
    """Schema for description generator response."""
    text: str = Field(..., description="Generated product description")
    status: str = Field(default="success", description="Status of the generation")
    model: str = Field(default="mistral", description="Model used for generation")
