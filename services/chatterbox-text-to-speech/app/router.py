from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from .schemas import GenerateAudioRequest
from .service import generate_audio

router = APIRouter()


@router.post("/generate-audio")
def generate_audio_endpoint(request: GenerateAudioRequest):
    """
    Endpoint to generate audio from text using the Chatterbox TTS model.
    
    Args:
        request: The request containing the text and optional audio prompt URL
        
    Returns:
        Audio file as WAV bytes
    """
    try:
        audio_bytes = generate_audio(request)
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=generated_audio.wav"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")
