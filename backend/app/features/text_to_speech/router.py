from fastapi import APIRouter, HTTPException, Body
import logging
from typing import List
from app.shared.schemas import WarmupRequest, ServiceResponse

logger = logging.getLogger(__name__)
from .schemas import (
    TextToSpeechRequest,
    VoiceModel
)
from .service import inference, warmup, list_available_voices

router = APIRouter()

@router.post(
    "/",
    response_model=ServiceResponse[dict],
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
async def generate_speech_proxy(
    request: TextToSpeechRequest = Body(
        ...,
        examples={
            "text": "Hello, this is a sample text that will be converted to speech using artificial intelligence.",
            "model": "chatterbox",
            "voice_url": "https://example.com/voice_sample.wav"
        }
    )
):
    try:
        return await inference(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")

@router.post(
    "/warmup",
    response_model=ServiceResponse[dict],
    summary="Warmup Model",
    description="Trigger warmup of a specific image description model. Returns status of the warmup process."
)
async def warmup_model(request: WarmupRequest):
    """Warmup a specific text generation model."""
    try:
        # Usar la función warmup que ya está importada al comienzo del archivo
        return await warmup(request.model)
    except Exception as e:
        # La función warmup ya maneja internamente los errores
        # Esto solo se ejecutaría si hay un error inesperado
        raise HTTPException(status_code=500, detail=f"Warmup failed for {request.model}: {str(e)}")

@router.get(
    "/voices",
    response_model=ServiceResponse[List[VoiceModel]],
    summary="Get Available Voice Models",
    description="Get a list of available voice models for voice cloning from the configuration file."
)
async def get_available_voices():
    """Get available voice models."""
    try:
        voices = await list_available_voices()
        return ServiceResponse(status="success", message="Available voices retrieved successfully", data=voices)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error retrieving available voices: {error_msg}")
        return ServiceResponse(
            status="error",
            message=f"Error retrieving available voices: {error_msg}",
            data=None
        )