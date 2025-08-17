from pydantic import BaseModel, Field
from typing import Optional

class GenerateAudioRequest(BaseModel):
    """Schema for audio generation request."""
    text: str = Field(..., description="Text to convert to speech")
    audio_prompt_url: Optional[str] = Field(None, description="Optional URL to audio prompt file")
