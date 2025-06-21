from fastapi import APIRouter, HTTPException
from app.generate_description.schemas import GenerateDescriptionRequest, GenerateDescriptionResponse
from app.generate_description.service import generate_description

router = APIRouter()


@router.post("/", response_model=GenerateDescriptionResponse)
async def generate_description_endpoint(request: GenerateDescriptionRequest):
    """
    Endpoint to generate description using Mistral.
    
    Args:
        request: The request containing the text and prompt
        
    Returns:
        The generated description
    """
    try:
        result = await generate_description(
            text=request.text,
            prompt=request.prompt,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate description: {str(e)}")
