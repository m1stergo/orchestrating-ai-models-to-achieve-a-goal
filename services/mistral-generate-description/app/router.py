from fastapi import APIRouter, HTTPException
from .schemas import GenerateDescriptionRequest, GenerateDescriptionResponse
from .service import generate_description

router = APIRouter()

@router.post("/generate-description", response_model=GenerateDescriptionResponse)
async def generate_description_endpoint(
    request: GenerateDescriptionRequest
):
    """
    Generate description using the Mistral model.
    
    Args:
        request: The request containing text and optional prompt
        
    Returns:
        The generated description
    """
    try:
        result = await generate_description(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate description: {str(e)}")


@router.get("/healthz")
async def readiness_check():
    """
    Readiness probe endpoint that checks if the model is loaded.
    Used by Kubernetes/RunPod to determine if the pod is ready to serve requests.
    """
    from .shared import model_loaded
    return {
        "status": "ready" if model_loaded else "loading",
        "loaded": model_loaded,
        "service": "generate-description"
    }


@router.get("/warmup")
async def warmup():
    """
    Endpoint to trigger model loading if not already loaded.
    Useful for manual warmup after deployment.
    """
    from . import shared
    
    if shared.model_loaded:
        return {"status": "already_loaded"}
    
    try:
        await shared.model_instance.is_loaded()
        shared.model_loaded = True
        return {"status": "loaded_successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")

