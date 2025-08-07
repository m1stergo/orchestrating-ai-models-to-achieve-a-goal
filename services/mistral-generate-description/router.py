from fastapi import APIRouter, HTTPException
from schemas import GenerateDescriptionRequest, GenerateDescriptionResponse
from service import generate_description

router = APIRouter()

@router.post("/generate-description", response_model=GenerateDescriptionResponse)
async def generate_description_endpoint(
    request: GenerateDescriptionRequest
):
    """
    Generate description using the Mistral model.
    
    Args:
        request: The request containing text and optional prompt
        
    Returns:
        The generated description
    """
    try:
        result = await generate_description(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate description: {str(e)}")

