from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    """Schema for image upload response."""
    filename: str
    content_type: str
    image_url: str
    size: int
