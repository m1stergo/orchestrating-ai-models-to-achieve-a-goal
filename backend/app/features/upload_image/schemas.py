"""Pydantic schemas for image upload functionality.

This module defines the data models used for image upload requests and responses.
These schemas provide validation and serialization for the API endpoints.
"""
from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    """Response model for image upload endpoint.
    
    This schema defines the structure of the response returned when an image
    is successfully uploaded through the API.
    
    Attributes:
        filename (str): The unique filename generated for the uploaded image
        content_type (str): The MIME type of the image (e.g., image/jpeg)
        image_url (str): The URL where the uploaded image can be accessed
        size (int): The size of the image file in bytes
    """
    filename: str
    content_type: str
    image_url: str
    size: int
