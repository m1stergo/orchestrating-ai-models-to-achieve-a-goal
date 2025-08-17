from pydantic import BaseModel, Field
from typing import Optional

class TextToSpeechRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    model: Optional[str] = Field(None, description="Preferred TTS model: 'chatterbox'")
    audio_prompt_url: Optional[str] = Field(None, description="Optional URL to audio prompt file for voice cloning")
    
class TextToSpeechResponse(BaseModel):
    audio_url: str = Field(..., description="URL to the generated audio file")