from pydantic import BaseModel, Field
from typing import Optional, List

class GenerateDescriptionRequest(BaseModel):
    image_description: str
    model: str = "openai"  # Default model
    prompt: Optional[str] = None

class GenerateDescriptionResponse(BaseModel):
    description: str

class GeneratePromotionalAudioScriptRequest(BaseModel):
    product_description: str
    model: str = "openai"  # Default model
    prompt: Optional[str] = None
    
class GeneratePromotionalAudioScriptResponse(BaseModel):
    script: str

class WarmupRequest(BaseModel):
    model: str

class HealthCheckRequest(BaseModel):
    model: str
