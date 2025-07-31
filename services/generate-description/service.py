import logging
from typing import List

from schemas import GenerateDescriptionRequest, GenerateDescriptionResponse
from strategies.factory import GenerateDescriptionStrategyFactory, strategy_factory

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
    Generate description using the specified or best available strategy.
    
    Args:
        request: The generation request containing text and optional strategy
        
    Returns:
        Generated description response with strategy_used
    """
    try:
        # Get strategy from request body
        strategy = GenerateDescriptionStrategyFactory.get_strategy(request.strategy)
        logger.info(f"Using strategy: {strategy.name}")
        
        # Check if strategy is available
        if not strategy.is_available():
            raise Exception(f"Strategy {strategy.name} is not available")
        
        # Format the hardcoded prompt with request data
        formatted_prompt = PROMPT_TEMPLATE.format(text=request.text)
        
        # Generate description
        generated_text = await strategy.generate_description(
            text="",  # Not needed since all info is in the prompt
            prompt=formatted_prompt
        )
        
        return GenerateDescriptionResponse(
            text=generated_text,
            strategy_used=strategy.name
        )
        
    except Exception as e:
        logger.error(f"Error generating description: {str(e)}")
        raise Exception(f"Text generation failed: {str(e)}")


async def get_available_strategies() -> List[dict]:
    """
    Get list of available text generation strategies.
    
    Returns:
        List of strategy information dictionaries
    """
    try:
        return await strategy_factory.get_available_strategies()
    except Exception as e:
        logger.error(f"Error getting available strategies: {str(e)}")
        return []
