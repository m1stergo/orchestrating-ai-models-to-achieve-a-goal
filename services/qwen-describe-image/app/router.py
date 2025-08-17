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
