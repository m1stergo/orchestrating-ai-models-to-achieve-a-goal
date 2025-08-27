from pydantic import BaseModel, Field
from typing import Optional, List

class GenerateDescriptionRequest(BaseModel):
    text: str = Field(..., description="Product information to generate description from")
    model: Optional[str] = Field(None, description="Preferred model: 'openai', 'gemini', or 'mistral'")
    prompt: Optional[str] = Field(None, description="Optional custom prompt for text generation")
    categories: Optional[List[str]] = Field(None, description="Array of available product categories")
    
class GenerateDescriptionResponse(BaseModel):
    text: str = Field(..., description="Generated product description")

class GeneratePromotionalAudioScriptRequest(BaseModel):
    text: str = Field(..., description="Marketing text to transform into promotional audio script")
    model: Optional[str] = Field(None, description="Preferred model: 'openai', 'gemini', or 'mistral'")
    prompt: Optional[str] = Field(None, description="Optional custom prompt for promotional script generation")
    
class GeneratePromotionalAudioScriptResponse(BaseModel):
    text: str = Field(..., description="Generated promotional audio script")
