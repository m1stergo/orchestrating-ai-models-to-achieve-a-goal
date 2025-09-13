from pydantic import BaseModel, Field
from typing import Optional

class TextToSpeechRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    model: Optional[str] = Field(None, description="Preferred TTS model: 'chatterbox'")
    voice_url: Optional[str] = Field(None, description="Optional URL to audio prompt file for voice cloning")

class VoiceModel(BaseModel):
    name: str = Field(..., description="Display name of the voice (usually the person name)")
    audio_url: str = Field(..., description="Public URL to the voice model audio sample")