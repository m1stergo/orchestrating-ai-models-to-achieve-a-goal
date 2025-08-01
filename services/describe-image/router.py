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


@router.get("/models")
async def list_available_models():
    """
    Endpoint to list all available image description models and their status.
    
    Returns:
        Dict with information about available models
    """
    try:
        models = await get_available_models()
        return {
            "models": models,
            "total": len(models),
            "available": len([m for m in models if m.get("available", False)]),
            "default_order": ["openai", "gemini", "qwen"],
            "usage": {
                "openai": "OpenAI GPT-4o Vision API (requires OPENAI_API_KEY)",
                "gemini": "Google Gemini Vision API (requires GOOGLE_API_KEY)",
                "qwen": "Local Qwen2.5-VL model (requires GPU resources)"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")
