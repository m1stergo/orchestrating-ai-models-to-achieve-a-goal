from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from .schemas import GenerateAudioRequest
from .service import generate_audio

router = APIRouter()

# Global variable to track model loading status
model_loaded = False


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


@router.get("/healthz")
async def readiness_check():
    """
    Readiness probe endpoint that checks if the model is loaded.
    Used by Kubernetes/RunPod to determine if the pod is ready to serve requests.
    """
    from .service import model_instance
    model_loaded = model_instance is not None
    return {
        "status": "ready" if model_loaded else "loading",
        "loaded": model_loaded,
        "service": "chatterbox-text-to-speech"
    }


@router.get("/warmup")
async def warmup():
    """
    Endpoint to trigger model loading if not already loaded.
    Useful for manual warmup after deployment.
    """
    from .service import load_model, model_instance
    
    if model_instance is not None:
        return {"status": "already_loaded"}
    
    try:
        load_model()
        return {"status": "loaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")
