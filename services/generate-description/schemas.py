from pydantic import BaseModel, Field
from typing import Optional


class GenerateDescriptionRequest(BaseModel):
    """Schema for description generator request."""
    text: str = Field(..., description="Product information to generate description from")
    strategy: Optional[str] = Field(None, description="Preferred strategy: 'openai', 'gemini', or 'mistral'. If not specified, uses the first available strategy.")
    

class GenerateDescriptionResponse(BaseModel):
    """Schema for description generator response."""
    text: str = Field(..., description="Generated product description")
    strategy_used: Optional[str] = Field(None, description="Strategy that was actually used to generate the description")
