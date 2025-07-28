from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import httpx
import os
from app.config import settings

router = APIRouter()

# Service URLs - these will be configured via environment variables
DESCRIBE_IMAGE_SERVICE_URL = os.getenv("DESCRIBE_IMAGE_SERVICE_URL", "http://localhost:8001")
EXTRACT_WEBCONTENT_SERVICE_URL = os.getenv("EXTRACT_WEBCONTENT_SERVICE_URL", "http://localhost:8002")
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
async def extract_webcontent_proxy(request_data: dict):
    """Proxy endpoint for extract web content service"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{EXTRACT_WEBCONTENT_SERVICE_URL}/api/v1/extract",
                json=request_data
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

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
    """Check health of all microservices"""
    services_status = {}
    
    services = {
        "describe-image": f"{DESCRIBE_IMAGE_SERVICE_URL}/health",
        "extract-webcontent": f"{EXTRACT_WEBCONTENT_SERVICE_URL}/health",
        "generate-description": f"{GENERATE_DESCRIPTION_SERVICE_URL}/health"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for service_name, health_url in services.items():
            try:
                response = await client.get(health_url)
                services_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": health_url
                }
            except Exception as e:
                services_status[service_name] = {
                    "status": "unreachable",
                    "error": str(e),
                    "url": health_url
                }
    
    return {"services": services_status}
