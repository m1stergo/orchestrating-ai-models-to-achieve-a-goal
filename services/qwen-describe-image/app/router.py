from fastapi import APIRouter, HTTPException
from .schemas import DescribeImageRequest, DescribeImageResponse
from .service import describe_image, warmup_model, get_service_status
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/describe-image", response_model=DescribeImageResponse)
async def describe_image_endpoint(request: DescribeImageRequest):
    """
    Main endpoint that handles all actions like RunPod handler.
    
    Actions:
    - warmup: Trigger model loading
    - status: Check model status
    - inference: Run image description (default)
    
    Args:
        request: The request containing action and optional image_url/prompt
        
    Returns:
        Response based on the action performed
    """
    action = request.action or "inference"
    
    logger.info(f"FastAPI handler called with action: {action}")
    
    try:
        if action == "warmup":
            result = warmup_model()
            return DescribeImageResponse(**result)
            
        elif action == "status":
            result = get_service_status()
            return DescribeImageResponse(**result)
            
        elif action == "inference":
            if not request.image_url:
                return DescribeImageResponse(
                    status="error",
                    message="image_url is required for inference action"
                )
            
            result = describe_image(request)
            return result
            
        else:
            return DescribeImageResponse(
                status="error",
                message=f"Unknown action: {action}. Valid actions: warmup, status, inference"
            )
            
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        return DescribeImageResponse(
            status="error",
            message=str(e)
        )
