from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel
from pydantic.generics import GenericModel

# Tipo genérico para el campo data
T = TypeVar('T')

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

# Modelo de respuesta estandarizado para APIs
class ServiceResponse(GenericModel, Generic[T]):
    status: str
    message: str
    data: Optional[T] = None