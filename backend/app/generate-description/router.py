from fastapi import APIRouter, HTTPException, Body
import httpx
from app.config import settings
from .schemas import (
    GenerateDescriptionRequest,
    GenerateDescriptionResponse
)
from pydantic import BaseModel
from typing import Dict, Any

class ServicesHealthResponse(BaseModel):
    services: Dict[str, Any]

router = APIRouter()

@router.post(
    "/",
    response_model=GenerateDescriptionResponse,
    responses={
        200: {
            "description": "Enhanced product description generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "text": "Experience cutting-edge technology with this premium smartphone featuring an elegant black finish. The device boasts a stunning large touchscreen display that delivers crystal-clear visuals, while the advanced multi-camera system captures professional-quality photos and videos. Perfect for both business professionals and tech enthusiasts who demand excellence in design and performance.",
                        "model": "openai"
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
    selecting the user's preferred AI model for content generation.
    
    **Supported models:**
    - `openai`: GPT-4 (creative, engaging copy)
    - `mistral`: Mistral AI (balanced, versatile content)
    - `gemini`: Google Gemini (balanced, versatile content)
    
    **Input Requirements:**
    - `text`: Product information to generate description from (required)
    - `model`: Preferred AI model - 'openai', 'gemini', or 'mistral' (required)
    """
)
async def generate_description_proxy(
    request: GenerateDescriptionRequest = Body(
        ...,
        example={
            "text": "A black smartphone with a large screen and multiple cameras",
            "model": "openai"
        }
    )
):
    try:
        # Direct proxy to the microservice
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.GENERATE_DESCRIPTION_SERVICE_URL}/generate-description/",
                json=request.model_dump()
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
