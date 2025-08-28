from fastapi import APIRouter, HTTPException, Body
import httpx
from app.config import settings
from .schemas import (
    GenerateDescriptionRequest,
    GenerateDescriptionResponse,
    GeneratePromotionalAudioScriptRequest,
    GeneratePromotionalAudioScriptResponse
)
from pydantic import BaseModel
from typing import Dict, Any, List

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
        # Call the service directly using the adapter pattern
        from .service import generate_description
        return await generate_description(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating description: {str(e)}")

@router.post(
    "/promotional-audio-script",
    response_model=GeneratePromotionalAudioScriptResponse,
    responses={
        200: {
            "description": "Promotional audio script generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "text": "Wait, you NEED to see this! This isn't just any smartphone - it's your new best friend! Black, sleek, and absolutely stunning with that massive screen that'll make you never want to look away. Plus those cameras? They're basically professional-level magic in your pocket! Ready to upgrade your life? Link in bio! #TechTok #SmartphoneGoals"
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
                        "service": "generate-promotional-audio-script"
                    }
                }
            }
        }
    },
    summary="Generate Promotional Audio Script",
    description="""
    Transform marketing text into an engaging script for Reels/TikTok promotional videos.
    
    This endpoint converts formal marketing copy into conversational, energetic content
    optimized for short-form social media videos under 30 seconds.
    
    **Supported models:**
    - `openai`: GPT-4 (creative, engaging scripts)
    - `mistral`: Mistral AI (balanced, versatile content)
    - `gemini`: Google Gemini (balanced, versatile content)
    
    **Output Features:**
    - Strong attention-grabbing hook
    - Natural, conversational tone
    - Short, punchy sentences
    - Social media expressions
    - Clear call-to-action
    """
)
async def generate_promotional_audio_script_proxy(
    request: GeneratePromotionalAudioScriptRequest = Body(
        ...,
        example={
            "text": "Premium smartphone with elegant black finish, large touchscreen display, and advanced multi-camera system for professional photos.",
            "model": "openai"
        }
    )
):
    try:
        # Call the service directly using the adapter pattern
        from .service import generate_promotional_audio_script
        return await generate_promotional_audio_script(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating promotional audio script: {str(e)}")

@router.post(
    "/warmup",
    summary="Warmup Mistral Model",
    description="Warmup the Mistral model for faster response times"
)
async def warmup_mistral_model():
    """Warmup the Mistral model."""
    try:
        from .service import warmup_mistral_service
        return await warmup_mistral_service()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error warming up Mistral model: {str(e)}")

@router.get(
    "/models",
    response_model=List[str],
    summary="Get Available Models",
    description="Get list of available models for description generation"
)
async def get_available_models():
    """Get available models for description generation."""
    return ["openai", "gemini", "mistral"]
