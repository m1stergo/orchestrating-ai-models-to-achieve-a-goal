from fastapi import APIRouter, HTTPException
from typing import List
from schemas import GenerateDescriptionRequest, GenerateDescriptionResponse
from service import generate_description, get_available_strategies

router = APIRouter()


@router.post("/", response_model=GenerateDescriptionResponse)
async def generate_description_endpoint(
    request: GenerateDescriptionRequest
):
    """
    Generate description using the specified or best available strategy.
    
    Args:
        request: The request containing text and optional strategy
        
    Returns:
        The generated description with strategy_used
    """
    try:
        result = await generate_description(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate description: {str(e)}")


@router.get("/strategies")
async def list_strategies():
    """
    Get list of available text generation strategies.
    
    Returns:
        List of available strategies with their information
    """
    try:
        strategies = await get_available_strategies()
        return {
            "strategies": strategies,
            "total": len(strategies),
            "available": len([s for s in strategies if s.get("available", False)])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strategies: {str(e)}")
