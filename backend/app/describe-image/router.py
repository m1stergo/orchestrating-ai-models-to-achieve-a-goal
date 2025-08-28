from fastapi import APIRouter, HTTPException, Body
from .schemas import (
    DescribeImageRequest,
    DescribeImageResponse,
)
from .service import describe_image, warmup_qwen_service
from typing import List

router = APIRouter()

@router.post(
    "/",
    response_model=DescribeImageResponse,
    responses={
        200: {
            "description": "Image description generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "description": "A modern smartphone with a sleek black design, featuring a large touchscreen display and multiple camera lenses on the back.",
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Service unavailable: Connection timeout",
                        "service": "describe-image"
                    }
                }
            }
        }
    },
    summary="Describe Image Content",
    description="""
    Generate a detailed description of an image using AI vision models.
    
    This endpoint uses adapter pattern to select the appropriate AI model
    (OpenAI GPT-4 Vision, Google Gemini Vision, or Qwen-VL).
    
    **Supported Models:**
    - `openai`: GPT-4 Vision (high accuracy, detailed descriptions)
    - `gemini`: Google Gemini Vision (fast processing, good for products)
    - `qwen`: Qwen-VL (local processing, privacy-focused)
    """
)
async def describe_image_proxy(
    request: DescribeImageRequest = Body(
        ...,
        example={
            "image_url": "https://example.com/product-image.jpg",
            "model": "openai"
        }
    )
):
    try:
        # Call the service directly using the adapter pattern
        return await describe_image(request)
    except Exception as e:
        error_message = str(e)
        # Check for specific Qwen errors and return appropriate status codes
        if "QWEN_NOT_READY" in error_message or "QWEN_SERVICE_DOWN" in error_message:
            raise HTTPException(status_code=503, detail=error_message)
        else:
            raise HTTPException(status_code=500, detail=f"Error describing image: {error_message}")

@router.post(
    "/warmup",
    summary="Warmup Qwen Model",
    description="Trigger warmup of the Qwen model service. Returns status of the warmup process."
)
async def warmup_qwen():
    """Warmup the Qwen model service."""
    try:
        result = await warmup_qwen_service()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Warmup failed: {str(e)}")

@router.get(
    "/models",
    response_model=List[str],
    summary="Get Available Models",
    description="Get list of available models for image description"
)
async def get_available_models():
    """Get available models for image description."""
    return ["openai", "gemini", "qwen"]
