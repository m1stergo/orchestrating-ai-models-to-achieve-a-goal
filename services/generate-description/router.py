from fastapi import APIRouter, HTTPException
from schemas import GenerateDescriptionRequest, GenerateDescriptionResponse
from service import generate_description, get_available_models

router = APIRouter()

@router.post("/generate-description/", response_model=GenerateDescriptionResponse)
async def generate_description_endpoint(
    request: GenerateDescriptionRequest
):
    """
    Generate description using the specified or best available model.
    
    Args:
        request: The request containing text and optional model
        
    Returns:
        The generated description with model_used
    """
    try:
        result = await generate_description(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate description: {str(e)}")


@router.get("/models/")
async def list_models():
    """
    Get list of available text generation models.
    
    Returns:
        List of available models with their information
    """
    try:
        model_names = await get_available_models()
        return model_names
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")
