from fastapi import APIRouter, HTTPException, Body
from .schemas import (
    TextToSpeechRequest,
    TextToSpeechResponse,
    VoiceModelsResponse
)
from pydantic import BaseModel
from typing import Dict, Any

class ServicesHealthResponse(BaseModel):
    services: Dict[str, Any]

router = APIRouter()

@router.post(
    "/",
    response_model=TextToSpeechResponse,
    responses={
        200: {
            "description": "Audio generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "audio_url": "http://localhost:8003/audio/generated_audio_123.wav"
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Service unavailable: Connection timeout",
                        "service": "text-to-speech"
                    }
                }
            }
        }
    },
    summary="Generate Speech from Text",
    description="""
    Convert text to speech using AI-powered text-to-speech models.
    
    This endpoint acts as a proxy to the chatterbox-text-to-speech microservice,
    providing high-quality voice synthesis with optional voice cloning capabilities.
    
    **Supported models:**
    - `chatterbox`: ChatterboxTTS (high-quality voice synthesis with voice cloning support)
    
    **Input Requirements:**
    - `text`: Text to convert to speech (required)
    - `model`: TTS model to use - currently supports 'chatterbox' (optional, defaults to 'chatterbox')
    - `voice_url`: URL to audio file for voice cloning (optional)
    """
)
async def generate_speech_proxy(
    request: TextToSpeechRequest = Body(
        ...,
        example={
            "text": "Hello, this is a sample text that will be converted to speech using artificial intelligence.",
            "model": "chatterbox",
            "voice_url": "https://example.com/voice_sample.wav"
        }
    )
):
    try:
        # Call the service directly using the adapter pattern
        from .service import generate_speech
        return await generate_speech(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")

@router.get(
    "/models",
    response_model=Dict[str, Any],
    summary="Get Available TTS Models",
    description="Get a list of available text-to-speech models and their capabilities."
)
async def get_available_models():
    """Get available TTS models."""
    try:
        from .service import get_available_models
        models = await get_available_models()
        return {
            "models": models,
            "default": "chatterbox"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting models: {str(e)}")

@router.get(
    "/voices",
    response_model=VoiceModelsResponse,
    summary="Get Available Voice Models",
    description="Get a list of available voice models for voice cloning from the configuration file."
)
async def get_available_voices():
    """Get available voice models."""
    try:
        from .service import list_available_voices
        voices = await list_available_voices()
        return VoiceModelsResponse(voices=voices, count=len(voices))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting voices: {str(e)}")
