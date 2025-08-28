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
    import logging
    from .shared import model_instance, model_loaded
    
    logger = logging.getLogger(__name__)
    
    if model_loaded:
        logger.info("Model already loaded")
        return {"status": "already_loaded", "loaded": True}
    
    try:
        logger.info("Starting model warmup...")
        await model_instance.is_loaded()
        
        # Update the global model_loaded flag
        import app.shared as shared
        shared.model_loaded = True
        
        logger.info("Model warmup completed successfully")
        return {"status": "loaded_successfully", "loaded": True}
    except Exception as e:
        logger.error(f"Model warmup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")
