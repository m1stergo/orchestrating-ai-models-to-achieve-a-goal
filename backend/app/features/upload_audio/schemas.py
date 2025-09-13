from pydantic import BaseModel


class AudioUploadResponse(BaseModel):
    """Schema for audio upload response."""
    filename: str
    content_type: str
    audio_url: str
    size: int
