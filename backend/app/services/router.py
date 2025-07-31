from fastapi import APIRouter, HTTPException, Body
import httpx
from app.extract_web_content.service import extract_web_content
from app.extract_web_content.schemas import ExtractWebContentRequest
from app.config import settings
from app.services.schemas import (
    DescribeImageResponse,
    GenerateDescriptionRequest,
    GenerateDescriptionResponse,
    ServicesHealthResponse,
    ErrorResponse
)

router = APIRouter()

@router.post(
    "/describe-image",
    response_model=DescribeImageResponse,
    responses={
        200: {
            "description": "Image description generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "description": "A modern smartphone with a sleek black design, featuring a large touchscreen display and multiple camera lenses on the back.",
                        "strategy_used": "openai"
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable",
            "model": ErrorResponse,
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
    selecting the user's preferred AI strategy (OpenAI GPT-4 Vision, Google Gemini Vision, or Qwen-VL).
    
    **Features:**
    - Automatic strategy selection based on user preferences
    - Support for image URLs
    - Multiple AI vision strategies available
    
    **Supported Strategies:**
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
            "strategy": "openai"
        }
    )
):
    try:
        # Direct proxy to the microservice
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{settings.DESCRIBE_IMAGE_SERVICE_URL}/api/v1/describe",
                json=request.model_dump()
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.post("/extract-webcontent")
async def extract_webcontent_proxy(request: ExtractWebContentRequest):
    """Extract web content using internal service"""
    try:
        # Use the internal extract_web_content service
        result = await extract_web_content(str(request.url))
        
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting web content: {str(e)}")

@router.post(
    "/generate-description",
    response_model=GenerateDescriptionResponse,
    responses={
        200: {
            "description": "Enhanced product description generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "text": "Experience cutting-edge technology with this premium smartphone featuring an elegant black finish. The device boasts a stunning large touchscreen display that delivers crystal-clear visuals, while the advanced multi-camera system captures professional-quality photos and videos. Perfect for both business professionals and tech enthusiasts who demand excellence in design and performance.",
                        "strategy_used": "openai"
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Service unavailable: Connection timeout",
                        "service": "generate-description"
                    }
                }
            }
        }
    },
    summary="Generate Enhanced Product Description",
    description="""
    Transform a basic image description into an engaging, marketing-ready product description.
    
    This endpoint acts as a proxy to the generate-description microservice, automatically
    selecting the user's preferred AI strategy for content generation.
    
    **Features:**
    - Automatic strategy selection based on user preferences
    - Marketing-focused content enhancement
    - Customizable writing style and tone
    - Word count optimization
    - SEO-friendly descriptions
    
    **Supported Strategies:**
    - `openai`: GPT-4 (creative, engaging copy)
    - `anthropic`: Claude (professional, detailed descriptions)
    - `gemini`: Google Gemini (balanced, versatile content)
    
    **Input Requirements:**
    - `image_description`: Basic description of the product/image
    - `product_context`: Optional context about the product category, brand, etc.
    - `style`: Optional style guide (e.g., "professional", "casual", "luxury")
    """
)
async def generate_description_proxy(
    request: GenerateDescriptionRequest = Body(
        ...,
        example={
            "text": "A black smartphone with a large screen and multiple cameras",
            "strategy": "openai"
        }
    )
):
    try:
        # Direct proxy to the microservice
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.GENERATE_DESCRIPTION_SERVICE_URL}/api/v1/generate",
                json=request.model_dump()
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.get(
    "/health",
    response_model=ServicesHealthResponse,
    responses={
        200: {
            "description": "Health status of all services",
            "content": {
                "application/json": {
                    "example": {
                        "services": {
                            "describe-image": {
                                "status": "healthy",
                                "type": "external",
                                "url": "http://describe-image-service:8001"
                            },
                            "generate-description": {
                                "status": "healthy",
                                "type": "external",
                                "url": "http://generate-description-service:8003"
                            },
                            "extract-webcontent": {
                                "status": "healthy",
                                "type": "internal",
                                "note": "Internal feature - no external dependency"
                            }
                        }
                    }
                }
            }
        }
    },
    summary="Check Services Health",
    description="""
    Monitor the health status of all microservices and internal features.
    
    This endpoint checks the availability and health of:
    - **External microservices**: describe-image, generate-description
    - **Internal features**: extract-webcontent
    
    **Service Types:**
    - `external`: Microservices running in separate containers
    - `internal`: Features integrated within the main backend
    
    **Health Status:**
    - `healthy`: Service is operational and responding
    - `unhealthy`: Service is not responding or returning errors
    
    Use this endpoint for monitoring, health checks, and debugging service connectivity issues.
    """
)
async def services_health():
    services_status = {}
    
    # External microservices to check
    external_services = {
        "describe-image": f"{settings.DESCRIBE_IMAGE_SERVICE_URL}/health",
        "generate-description": f"{settings.GENERATE_DESCRIPTION_SERVICE_URL}/health"
    }
    
    # Check external microservices
    async with httpx.AsyncClient(timeout=10.0) as client:
        for service_name, health_url in external_services.items():
            try:
                response = await client.get(health_url)
                services_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": health_url,
                    "type": "external"
                }
            except Exception as e:
                services_status[service_name] = {
                    "status": "unreachable",
                    "error": str(e),
                    "url": health_url,
                    "type": "external"
                }
    
    # Check internal extract-webcontent feature
    try:
        # Simple test to verify the internal service is working
        from app.extract_web_content.strategies.factory import StrategyFactory
        # If we can import and access the factory, the service is healthy
        services_status["extract-webcontent"] = {
            "status": "healthy",
            "type": "internal",
            "note": "Internal feature - no external dependency"
        }
    except Exception as e:
        services_status["extract-webcontent"] = {
            "status": "unhealthy",
            "error": str(e),
            "type": "internal"
        }
    
    return {"services": services_status}
