from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ProductBase(BaseModel):
    """Base schema for Product."""
    sku: str = Field(..., description="SKU of the product")
    name: str = Field(..., description="Name of the product")
    description: Optional[str] = Field(None, description="Description of the product")
    keywords: Optional[List[str]] = Field(None, description="List of keywords")
    category: Optional[str] = Field(None, description="Product category")
    images: Optional[List[str]] = Field(None, description="List of image URLs")
    audio_description: Optional[str] = Field(None, description="Audio description")
    audio: Optional[str] = Field(None, description="Audio URL")
    audio_config: Optional[Dict[str, str]] = Field(None, description="Audio configuration settings")
    additional_context: Optional[List[Dict[str, str]]] = Field(None, description="List of key-value pairs for additional context")
    image_description: Optional[str] = Field(None, description="Description generated from image")
    vendor_url: Optional[str] = Field(None, description="URL to vendor website")
    vendor_context: Optional[str] = Field(None, description="Context from vendor")
    selected_context_source: Optional[str] = Field(None, description="Source of context (image/website)")
    uploaded_image: Optional[str] = Field(None, description="URL to uploaded image")


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    sku: Optional[str] = Field(None, description="SKU of the product")
    name: Optional[str] = Field(None, description="Name of the product")
    description: Optional[str] = Field(None, description="Description of the product")
    keywords: Optional[List[str]] = Field(None, description="List of keywords")
    category: Optional[str] = Field(None, description="Product category")
    images: Optional[List[str]] = Field(None, description="List of image URLs")
    audio_description: Optional[str] = Field(None, description="Audio description")
    audio: Optional[str] = Field(None, description="Audio URL")
    audio_config: Optional[Dict[str, str]] = Field(None, description="Audio configuration settings")
    additional_context: Optional[List[Dict[str, str]]] = Field(None, description="List of key-value pairs for additional context")
    image_description: Optional[str] = Field(None, description="Description generated from image")
    vendor_url: Optional[str] = Field(None, description="URL to vendor website")
    vendor_context: Optional[str] = Field(None, description="Context from vendor")
    selected_context_source: Optional[str] = Field(None, description="Source of context (image/website)")
    uploaded_image: Optional[str] = Field(None, description="URL to uploaded image")


class ProductInDB(ProductBase):
    """Schema for a product in the database."""
    id: int = Field(..., description="Unique identifier for the product")
    
    class Config:
        from_attributes = True


class ProductResponse(ProductInDB):
    """Schema for product response."""
    pass



class ExportResponse(BaseModel):
    """Response schema for export operations."""
    
    filename: str
    download_url: str
    size: int
    products_count: int
    images_count: int
    audio_count: int