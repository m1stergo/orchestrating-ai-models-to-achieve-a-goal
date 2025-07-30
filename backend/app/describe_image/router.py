from fastapi import APIRouter, HTTPException
from app.describe_image.schemas import DescribeImageRequest, DescribeImageResponse
from app.describe_image.service import describe_image, get_available_strategies

router = APIRouter()


@router.post("/", response_model=DescribeImageResponse)
async def describe_image_endpoint(request: DescribeImageRequest):
    """
    Endpoint to describe an image using the specified or default strategy.
    
    Args:
        request: The request containing the image URL and optional strategy preference
        
    Returns:
        The image description results with information about which strategy was used
    """
    try:
        result = await describe_image(
            request.image_url,
            preferred_strategy=request.strategy
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to describe image: {str(e)}")


@router.get("/strategies")
async def list_available_strategies():
    """
    Endpoint to list all available image description strategies and their status.
    
    Returns:
        Dict with information about available strategies
    """
    try:
        strategies = get_available_strategies()
        return {
            "available_strategies": strategies,
            "default_order": ["qwen", "openai"],
            "usage": {
                "qwen": "Local Qwen2.5-VL model (requires GPU/CPU resources)",
                "openai": "OpenAI GPT-4 Vision API (requires OPENAI_API_KEY)"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strategies: {str(e)}")
