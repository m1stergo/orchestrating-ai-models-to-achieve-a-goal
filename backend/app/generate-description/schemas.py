from pydantic import BaseModel
from typing import Optional, List, TypeVar, Generic

T = TypeVar('T')

class GenerateDescriptionRequest(BaseModel):
    text: str
    model: str = "openai"  # Default model
    prompt: Optional[str] = None
    categories: Optional[List[str]] = None

class ServiceResponse(BaseModel, Generic[T]):
    status: str
    message: str
    data: Optional[T] = None

class GeneratePromotionalAudioScriptRequest(BaseModel):
    product_description: str
    model: str = "openai"  # Default model
    prompt: Optional[str] = None

class WarmupRequest(BaseModel):
    model: str

class HealthCheckRequest(BaseModel):
    model: str
