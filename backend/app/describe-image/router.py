from fastapi import APIRouter
from typing import List
from .schemas import (
    DescribeImageRequest, WarmupRequest, StatusRequest,
    StandardResponse, ResponseDetails
)
from .service import describe_image, warmup, status
from fastapi import Body

router = APIRouter()

@router.post(
    "/run",
    response_model=StandardResponse,
    responses={
        200: {
            "description": "Image description generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "COMPLETED",
                        "id": "example-id",
                        "details": {
                            "status": "IDLE",
                            "message": "",
                            "data": "A modern smartphone with a sleek black design, featuring a large touchscreen display and multiple camera lenses on the back."
                        }
                    }
                }
            }
        },
        500: {
            "description": "Service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ERROR",
                        "id": None,
                        "details": {
                            "status": "ERROR",
                            "message": "Service unavailable: Connection timeout",
                            "data": ""
                        }
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
) -> StandardResponse:
    # Validate and return the standardized response
    return await describe_image(request)

@router.post(
    "/warmup",
    response_model=StandardResponse,
    summary="Warmup Model",
    description="Trigger warmup of a specific image description model. Returns status of the warmup process."
)
async def warmup_model(request: WarmupRequest) -> StandardResponse:
    """Warmup a specific image description model."""
    try:
        return await warmup(request.model)
    except Exception as e:
        return StandardResponse(
            status="ERROR",
            id=None,
            details=ResponseDetails(
                status="ERROR",
                message=f"Warmup failed for {request.model}: {str(e)}",
                data=""
            )
        )

@router.post(
    "/status",
    response_model=StandardResponse,
    summary="Check Model Status",
    description="Check the status of a specific model adapter. For Qwen, this checks if the service is ready and can optionally check a specific job ID."
)
async def check_status(request: StatusRequest) -> StandardResponse:
    """Check status of a specific model adapter."""
    try:
        return await status(request.model, request.job_id)
    except Exception as e:
        return StandardResponse(
            status="ERROR",
            id=None,
            details=ResponseDetails(
                status="ERROR",
                message=f"Status check failed for {request.model}: {str(e)}",
                data=""
            )
        )

@router.get(
    "/models",
    response_model=List[str],
    summary="Get Available Models",
    description="Get list of available models for image description"
)
async def get_available_models():
    """Get available models for image description."""
    return ["openai", "gemini", "qwen"]
