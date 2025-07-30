from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import httpx
import os
from app.extract_web_content.service import extract_web_content
from app.extract_web_content.schemas import ExtractWebContentRequest

router = APIRouter()

# Service URLs - these will be configured via environment variables
DESCRIBE_IMAGE_SERVICE_URL = os.getenv("DESCRIBE_IMAGE_SERVICE_URL", "http://localhost:8001")
GENERATE_DESCRIPTION_SERVICE_URL = os.getenv("GENERATE_DESCRIPTION_SERVICE_URL", "http://localhost:8003")

@router.post("/describe-image")
async def describe_image_proxy(
    image: UploadFile = File(...),
    prompt: Optional[str] = Form(None)
):
    """Proxy endpoint for describe image service"""
    try:
        # Prepare the files and data for the request
        files = {"image": (image.filename, await image.read(), image.content_type)}
        data = {"prompt": prompt} if prompt else {}
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{DESCRIBE_IMAGE_SERVICE_URL}/api/v1/describe",
                files=files,
                data=data
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

@router.post("/generate-description")
async def generate_description_proxy(request_data: dict):
    """Proxy endpoint for generate description service"""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{GENERATE_DESCRIPTION_SERVICE_URL}/api/v1/generate",
                json=request_data
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.get("/health")
async def services_health():
    """Check health of all services (external microservices and internal features)"""
    services_status = {}
    
    # External microservices to check
    external_services = {
        "describe-image": f"{DESCRIBE_IMAGE_SERVICE_URL}/health",
        "generate-description": f"{GENERATE_DESCRIPTION_SERVICE_URL}/health"
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
