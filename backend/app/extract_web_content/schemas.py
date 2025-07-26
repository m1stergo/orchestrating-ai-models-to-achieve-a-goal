from pydantic import BaseModel, HttpUrl


class ExtractWebContentRequest(BaseModel):
    """Schema for web content extraction request."""
    url: HttpUrl
    
    
class ExtractWebContentResponse(BaseModel):
    """Schema for web content extraction response."""
    url: str
    title: str
    keywords: list
    description: str
    images: list
