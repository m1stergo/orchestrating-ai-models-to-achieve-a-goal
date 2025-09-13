from fastapi import APIRouter, Body, HTTPException
from typing import List
from app.shared.schemas import GenerateDescriptionRequest, ServiceResponse, WarmupRequest
from .service import inference_text, inference_promotional_audio_script, get_available_models, warmup

router = APIRouter()

@router.post(
    "/",
    response_model=ServiceResponse[str],
    responses={
        200: {
            "description": "Enhanced product description generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "example": {
                        "status": "success",
                        "message": "Image description generated successfully",
                        "data": "Experience cutting-edge technology with this premium smartphone featuring an elegant black finish. The device boasts a stunning large touchscreen display that delivers crystal-clear visuals, while the advanced multi-camera system captures professional-quality photos and videos. Perfect for both business professionals and tech enthusiasts who demand excellence in design and performance.",
                        }
                    }
                }
            }
        },
        503: {
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
    summary="Generate Enhanced Product Description",
    description="""
    Transform a basic image description into an engaging, marketing-ready product description.
    
    This endpoint acts as a proxy to the generate_description microservice, automatically
    selecting the user's preferred AI model for content generation.
    
    **Supported models:**
    - `openai`: GPT-4 (creative, engaging copy)
    - `mistral`: Mistral AI (balanced, versatile content)
    - `gemini`: Google Gemini (balanced, versatile content)
    """
)
async def run_generate_description(
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
        return await inference_text(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating description: {str(e)}")

@router.post(
    "/promotional-audio-script",
    response_model=ServiceResponse,
    responses={
        200: {
            "description": "Promotional audio script generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Image description generated successfully",
                        "data": "Wait, you NEED to see this! This isn't just any smartphone - it's your new best friend! Black, sleek, and absolutely stunning with that massive screen that'll make you never want to look away. Plus those cameras? They're basically professional-level magic in your pocket! Ready to upgrade your life? Link in bio! #TechTok #SmartphoneGoals"
                    }
                }
            }
        },
        503: {
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
    summary="Generate Promotional Audio Script",
    description="""
    Transform marketing text into an engaging script for Reels/TikTok promotional videos.
    
    This endpoint converts formal marketing copy into conversational, energetic content
    optimized for short-form social media videos under 30 seconds.
    
    **Supported models:**
    - `openai`: GPT-4 (creative, engaging scripts)
    - `mistral`: Mistral AI (balanced, versatile content)
    - `gemini`: Google Gemini (balanced, versatile content)
    """
)
async def run_generate_promotional_audio_script(
    request: GenerateDescriptionRequest = Body(
        ...,
        example={
            "text": "Premium smartphone with elegant black finish, large touchscreen display, and advanced multi-camera system for professional photos.",
            "model": "openai"
        }
    )
):
    try:
        return await inference_promotional_audio_script(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating promotional audio script: {str(e)}")

@router.post(
    "/warmup",
    response_model=ServiceResponse[dict],
    summary="Warmup Model",
    description="Trigger warmup of a specific text generation model. Returns status of the warmup process."
)
async def warmup_model(request: WarmupRequest):
    """Warmup a specific text generation model."""
    try:
        result = await warmup(request.model)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Warmup failed for {request.model}: {str(e)}")

@router.get(
    "/models",
    response_model=ServiceResponse[List[str]],
    summary="Get Available Models",
    description="Get list of available models for description generation"
)
async def get_models():
    """Get available models for description generation."""
    return await get_available_models()
