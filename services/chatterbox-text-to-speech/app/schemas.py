from pydantic import BaseModel, Field
from typing import Optional

class GenerateAudioRequest(BaseModel):
    """Schema for audio generation request."""
    text: str = Field(..., description="Text to convert to speech")
    voice_url: Optional[str] = Field(None, description="Optional URL to audio prompt file")
    text_prompt: Optional[str] = Field(None, description="Optional custom prompt for text processing before TTS")
