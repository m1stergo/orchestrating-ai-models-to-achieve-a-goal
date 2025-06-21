from fastapi import APIRouter, HTTPException
from app.describe_image.schemas import DescribeImageRequest, DescribeImageResponse
from app.describe_image.service import describe_image

router = APIRouter()


@router.post("/", response_model=DescribeImageResponse)
async def describe_image_endpoint(request: DescribeImageRequest):
    """
    Endpoint to describe an image using Qwen.
    
    Args:
        request: The request containing the image URL and analysis options
        
    Returns:
        The image description results
    """
    try:
        result = await describe_image(
            request.image_url,
            analyze_objects=request.analyze_objects,
            analyze_faces=request.analyze_faces,
            analyze_text=request.analyze_text
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to describe image: {str(e)}")
