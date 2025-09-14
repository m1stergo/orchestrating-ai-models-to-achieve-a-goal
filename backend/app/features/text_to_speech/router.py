from fastapi import APIRouter, HTTPException
from typing import List
from app.shared.schemas import WarmupRequest, ServiceResponse
from .schemas import TextToSpeechRequest, VoiceModel
from .adapters.factory import TextToSpeechAdapterFactory

router = APIRouter()

@router.post(
    "/",
    response_model=ServiceResponse[str],
    responses={
        200: {
            "description": "Audio generated successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "audio_url": "http://localhost:8003/audio/generated_audio_123.wav"
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable",
            "content": {
                "application/json": {
                    "examples": {
                        "detail": "Service unavailable: Connection timeout",
                        "service": "text_to_speech"
                    }
                }
            }
        }
    },
    summary="Generate Speech from Text",
    description="""
    Convert text to speech using AI-powered text_to_speech models.
    
    This endpoint acts as a proxy to the chatterbox-text_to_speech microservice,
    providing high-quality voice synthesis with optional voice cloning capabilities.
    
    **Supported models:**
    - `chatterbox`: ChatterboxTTS (high-quality voice synthesis with voice cloning support)
    
    **Input Requirements:**
    - `text`: Text to convert to speech (required)
    - `model`: TTS model to use - currently supports 'chatterbox' (optional, defaults to 'chatterbox')
    - `voice_url`: URL to audio file for voice cloning (optional)
    """
)
async def run(
    request: TextToSpeechRequest
):
    try:
        adapter = TextToSpeechAdapterFactory.get_adapter(request.model)
        result = await adapter.infer(request.text, request.voice_url)
        return result
       
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")

@router.post(
    "/warmup",
    response_model=ServiceResponse[str],
    summary="Warmup Model",
    description="Trigger warmup of a specific image description model. Returns status of the warmup process."
)
async def warmup(request: WarmupRequest):
    """Warmup a specific text generation model."""
    try:
        adapter = TextToSpeechAdapterFactory.get_adapter(request.model)
        result = await adapter.warmup()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Warmup failed for {request.model}: {str(e)}")

@router.get(
    "/voices",
    response_model=ServiceResponse[List[VoiceModel]],
    summary="Get Available Voice Models",
    description="Get a list of available voice models for voice cloning from the configuration file."
)
def voices():
    """Get available voice models."""
    return TextToSpeechAdapterFactory.list_available_voices()
