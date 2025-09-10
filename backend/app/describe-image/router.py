from fastapi import APIRouter, Body, HTTPException
from typing import List
from app.shared.schemas import (
    DescribeImageRequest, WarmupRequest, ServiceResponse
)
from .service import inference, warmup, get_available_models

router = APIRouter()

@router.post(
    "/",
    response_model=ServiceResponse[str],
    responses={
        200: {
            "description": "Image description generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Image description generated successfully",
                        "data": "A modern smartphone with a sleek black design, featuring a large touchscreen display and multiple camera lenses on the back."
                    }
                }
            }
        },
        500: {
            "description": "Service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Service unavailable: Connection timeout",
                        "data": None
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
async def run_describe_image(
    request: DescribeImageRequest = Body(
        ...,
        example={
            "image_url": "https://example.com/product-image.jpg",
            "model": "openai"
        }
    )
):
    try:
        return await inference(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error describing image: {str(e)}")

@router.post(
    "/warmup",
    response_model=ServiceResponse[str],
    summary="Warmup Model",
    description="Trigger warmup of a specific image description model. Returns status of the warmup process."
)
async def warmup_model(request: WarmupRequest):
    """Warmup a specific text generation model."""
    try:
        # Usar la función warmup que ya está importada al comienzo del archivo
        return await warmup(request.model)
    except Exception as e:
        # La función warmup ya maneja internamente los errores
        # Esto solo se ejecutaría si hay un error inesperado
        raise HTTPException(status_code=500, detail=f"Warmup failed for {request.model}: {str(e)}")

@router.get(
    "/models",
    response_model=ServiceResponse[List[str]],
    summary="Get Available Models",
    description="Get list of available models for image description"
)
async def get_models():
    """Get available models for image description."""
    return await get_available_models()
