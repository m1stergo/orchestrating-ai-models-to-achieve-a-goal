from pydantic import BaseModel, Field
from typing import Optional

class GenerateDescriptionRequest(BaseModel):
    text: str = Field(..., description="Product information to generate description from")
    model: Optional[str] = Field(None, description="Preferred model: 'openai', 'gemini', or 'mistral'")
    prompt: Optional[str] = Field(None, description="Optional custom prompt for text generation")
    
class GenerateDescriptionResponse(BaseModel):
    description: str = Field(..., description="Generated product description")
