"""
Shared prompts for image description services.
"""
from typing import Optional


def get_image_description_prompt(custom_prompt: Optional[str] = None) -> str:
    """
    Get image description prompt template.
    
    Args:
        custom_prompt: Optional custom prompt from user settings
        
    Returns:
        str: The prompt template
    """
    if custom_prompt and custom_prompt.strip():
        return custom_prompt
        
    return """Analyze the main product in the image provided. Focus exclusively on the product itself. Based on your visual analysis of the product, complete the following template:

Image description: A brief but comprehensive visual description of the item, detailing its color, shape, material, and texture.
Product type: What is the object?
Material: What is it made of? Be specific if possible (e.g., "leather," "plastic," "wood").
Keywords: List relevant keywords that describe the item's appearance or function."""
