from fastapi import APIRouter, HTTPException, Body
import httpx
from app.config import settings
from .schemas import (
    DescribeImageRequest,
    DescribeImageResponse,
)

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
    
    This endpoint acts as a proxy to the describe-image microservice, automatically
    selecting the user's preferred AI model (OpenAI GPT-4 Vision, Google Gemini Vision, or Qwen-VL).
    
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
        # Direct proxy to the microservice
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{settings.DESCRIBE_IMAGE_SERVICE_URL}/describe-image/",
                json=request.model_dump()
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
