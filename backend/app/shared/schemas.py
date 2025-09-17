from typing import Optional, Generic, TypeVar, List, Literal
from pydantic import BaseModel
# No necesitamos importar GenericModel, ahora BaseModel es suficiente

# Tipo genérico para el campo data
T = TypeVar('T')

InferenceStatus = Literal["COMPLETED", "IN_PROGRESS", "FAILED", "COLD", "WARMINGUP", "IN_QUEUE"]

# API Request schemas
class GenerateDescriptionRequest(BaseModel):
    model: str = "openai"
    text: str
    prompt: Optional[str] = None
    categories: Optional[List[str]] = None

class DescribeImageRequest(BaseModel):
    model: str = "openai"
    image_url: str
    prompt: Optional[str] = None
    
class WarmupRequest(BaseModel):
    model: str

class StatusRequest(BaseModel):
    model: str
    job_id: Optional[str] = None

class ServiceResponse(BaseModel, Generic[T]):
    status: InferenceStatus
    message: str
    data: Optional[T] = None

class PodResponse(BaseModel, Generic[T]):
    status: InferenceStatus
    id: str
    output: ServiceResponse[T]
