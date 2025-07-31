from fastapi import APIRouter, HTTPException
from schemas import DescribeImageRequest, DescribeImageResponse
from service import describe_image, get_available_strategies

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
        result = await describe_image(request)
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
        strategies = await get_available_strategies()
        return {
            "strategies": strategies,
            "total": len(strategies),
            "available": len([s for s in strategies if s.get("available", False)]),
            "default_order": ["openai", "gemini", "qwen"],
            "usage": {
                "openai": "OpenAI GPT-4o Vision API (requires OPENAI_API_KEY)",
                "gemini": "Google Gemini Vision API (requires GOOGLE_API_KEY)",
                "qwen": "Local Qwen2.5-VL model (requires GPU/CPU resources)"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strategies: {str(e)}")
