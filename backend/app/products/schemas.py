from pydantic import BaseModel, Field
from typing import List, Optional


class ProductBase(BaseModel):
    """Base schema for Product."""
    name: str = Field(..., description="Name of the product")
    description: Optional[str] = Field(None, description="Description of the product")
    images: Optional[List[str]] = Field(None, description="List of image URLs")
    audio: Optional[str] = Field(None, description="Audio URL")


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, description="Name of the product")
    description: Optional[str] = Field(None, description="Description of the product")
    images: Optional[List[str]] = Field(None, description="List of image URLs")
    audio: Optional[str] = Field(None, description="Audio URL")


class ProductInDB(ProductBase):
    """Schema for a product in the database."""
    id: int = Field(..., description="Unique identifier for the product")
    
    class Config:
        orm_mode = True


class ProductResponse(ProductInDB):
    """Schema for product response."""
    pass
