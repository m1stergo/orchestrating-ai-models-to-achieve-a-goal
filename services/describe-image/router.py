from fastapi import APIRouter, HTTPException
from schemas import DescribeImageRequest, DescribeImageResponse
from service import describe_image, get_available_models

router = APIRouter()


@router.post("/describe-image/", response_model=DescribeImageResponse)
async def describe_image_endpoint(request: DescribeImageRequest):
    """
    Endpoint to describe an image using the specified or default model.
    
    Args:
        request: The request containing the image URL and optional model preference
        
    Returns:
        The image description results with information about which model was used
    """
    try:
        result = await describe_image(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to describe image: {str(e)}")


@router.get("/models/")
async def list_available_models():
    """
    Endpoint to list all available image description models.
    
    Returns:
        Array of available model names
    """
    try:
        # Now get_available_models returns a simple array of strings (model names)
        model_names = await get_available_models()
        return model_names
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")
