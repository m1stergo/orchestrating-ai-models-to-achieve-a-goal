from pydantic import BaseModel, Field
from typing import Optional, List

class TextToSpeechRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    model: Optional[str] = Field(None, description="Preferred TTS model: 'chatterbox'")
    audio_prompt_url: Optional[str] = Field(None, description="Optional URL to audio prompt file for voice cloning")
    
class TextToSpeechResponse(BaseModel):
    audio_url: str = Field(..., description="URL to the generated audio file")

class VoiceModel(BaseModel):
    name: str = Field(..., description="Display name of the voice (usually the person name)")
    audio_url: str = Field(..., description="Public URL to the voice model audio sample")

class VoiceModelsResponse(BaseModel):
    voices: List[VoiceModel] = Field(..., description="List of available voice models")
    count: int = Field(..., description="Total number of available voice models")