from fastapi import APIRouter, HTTPException
from .schemas import DescribeImageRequest, DescribeImageResponse
from .service import describe_image

router = APIRouter()


@router.post("/describe-image", response_model=DescribeImageResponse)
async def describe_image_endpoint(request: DescribeImageRequest):
    """
    Endpoint to describe an image using the Qwen VL model.
    
    Args:
        request: The request containing the image URL and optional prompt
        
    Returns:
        The image description results
    """
    try:
        result = await describe_image(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to describe image: {str(e)}")


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
        "service": "describe-image"
    }


@router.get("/warmup")
async def warmup():
    """
    Endpoint to trigger model loading if not already loaded.
    Useful for manual warmup after deployment.
    """
    from .shared import model_instance, model_loaded
    
    if model_loaded:
        return {"status": "already_loaded"}
    
    try:
        await model_instance.is_loaded()
        return {"status": "loaded_successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")
