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


@router.get("/status")
async def check_status():
    """
    Readiness probe endpoint that checks if the model is loaded and shows GPU information.
    Used by Kubernetes/RunPod to determine if the pod is ready to serve requests.
    """
    from .service import get_service_status
    return get_service_status()


@router.get("/warmup")
async def warmup():
    """
    Endpoint to trigger model loading if not already loaded.
    Useful for manual warmup after deployment.
    """
    from .service import warmup_model
    
    try:
        result = await warmup_model()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
