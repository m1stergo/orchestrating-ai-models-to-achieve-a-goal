import logging
from typing import List

from schemas import GenerateDescriptionRequest, GenerateDescriptionResponse
from ai_models.factory import GenerateDescriptionModelFactory

logger = logging.getLogger(__name__)

# Hardcoded prompt template
PROMPT_TEMPLATE = """
You are a professional e-commerce copywriter. Write a compelling product description based on the information below.

{text}

Write a clear, persuasive, English description of the product.
"""


async def generate_description(
    request: GenerateDescriptionRequest
) -> GenerateDescriptionResponse:
    """
    Generate description using the specified or best available model.
    
    Args:
        request: The generation request containing text and optional model
        
    Returns:
        Generated description response with model_used
    """
    try:
        # Get model from request body
        model = GenerateDescriptionModelFactory.get_model(request.model)
        
        # Check if model is available
        if not model.is_available():
            raise Exception(f"Model {model.name} is not available")
        
        # Format the hardcoded prompt with request data
        formatted_prompt = PROMPT_TEMPLATE.format(text=request.text)
        
        # Generate description
        generated_text = await model.generate_description(
            text="",  # Not needed since all info is in the prompt
            prompt=formatted_prompt
        )
        
        return GenerateDescriptionResponse(
            text=generated_text
        )
        
    except Exception as e:
        logger.error(f"Error generating description: {str(e)}")
        raise Exception(f"Text generation failed: {str(e)}")


async def get_available_models() -> List[dict]:
    """
    Get list of available text generation models.
    
    Returns:
        List of model information dictionaries
    """
    try:
        return GenerateDescriptionModelFactory.list_keys()
    except Exception as e:
        logger.error(f"Error getting available models: {str(e)}")
        return []
