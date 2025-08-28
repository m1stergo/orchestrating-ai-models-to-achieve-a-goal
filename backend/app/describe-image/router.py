from fastapi import APIRouter, HTTPException
from typing import List
from .schemas import DescribeImageRequest, DescribeImageResponse, WarmupRequest, HealthCheckRequest
from .service import describe_image, warmup_qwen_service
from fastapi import Body

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
    summary="Warmup Model",
    description="Trigger warmup of a specific image description model. Returns status of the warmup process."
)
async def warmup_model(request: WarmupRequest):
    """Warmup a specific image description model."""
    try:
        from .service import warmup_service
        result = await warmup_service(request.model)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Warmup failed for {request.model}: {str(e)}")

@router.post(
    "/healthz",
    summary="Health Check for Model",
    description="Check health status of a specific image description adapter"
)
async def health_check_model(request: HealthCheckRequest):
    """Check health status of a specific image description adapter."""
    try:
        from .service import health_check_service
        result = await health_check_service(request.model)
        # Return appropriate HTTP status based on health
        if result["status"] == "healthy":
            return result  # HTTP 200
        elif result["status"] == "loading":
            raise HTTPException(status_code=202, detail=result)
        else:
            # Everything else (unhealthy, error, unknown) is 503
            raise HTTPException(status_code=503, detail=result)
    except HTTPException:
        raise
    except Exception as e:
        # If we can't even call the service, it's definitely unavailable
        error_detail = {
            "status": "error",
            "message": f"Service completely unavailable for {request.model}",
            "details": str(e)
        }
        raise HTTPException(status_code=503, detail=error_detail)

@router.get(
    "/models",
    response_model=List[str],
    summary="Get Available Models",
    description="Get list of available models for image description"
)
async def get_available_models():
    """Get available models for image description."""
    return ["openai", "gemini", "qwen"]
