"""
Shared prompt templates for text generation adapters.
"""
from typing import Optional

def get_product_description_prompt(custom_prompt: str = None) -> str:
    """
    Get the product description prompt template.
    
    Args:
        custom_prompt: Optional custom prompt to use instead of default
        
    Returns:
        str: The prompt template with placeholders
    """
    base_instruction = custom_prompt if custom_prompt and custom_prompt.strip() else """
    You are a professional e-commerce copywriter.
    Write a short, concise product description for the following text:
    __description__

    Rules:
    - Title must be concise, clear, and descriptive (max 10 words)
    - Description must be direct, simple, and factual (40-60 words max)
    - Use short sentences, avoid marketing fluff and adjectives like "elevate", "charming", "whimsy"
    - Focus on features first, then benefits
    - Keywords must not repeat, must be relevant for SEO
    """

    json_structure = """Return a valid JSON response with the following structure:
    {
    "title": "Inferred product title/name",
    "description": "product description",
    "keywords": ["5 relevant SEO keywords, 1-3 words each, lowercase"],
    "category": "Suggested product category from this list: [{__categories__}]"
    }"""

    return base_instruction + json_structure


def get_promotional_audio_script_prompt(custom_prompt: Optional[str] = None) -> str:
    """
    Get promotional audio script prompt template.
    
    Args:
        custom_prompt: Optional custom prompt from user settings
        
    Returns:
        str: The prompt template
    """
    if custom_prompt and custom_prompt.strip():
        return custom_prompt
        
    return """
    Create a short description for a Reels/TikTok promotional video.
    The result should sound natural, conversational, and energetic, with short, punchy sentences that grab attention in the first few seconds.
    Include a strong hook at the beginning, a simple middle part, and a call-to-action at the end.
    Avoid being too formal, use common social media expressions, and keep the length suitable for a video under 30 seconds.
    Do not use emojis!
    
    Transform the following text: __description__
    """




def build_final_prompt(template: str, text: str, categories: list = None) -> str:
    """
    Build the final prompt by replacing placeholders.
    
    Args:
        template: The prompt template with placeholders
        text: The text to process
        categories: Optional list of categories
        
    Returns:
        str: The final prompt with placeholders replaced
    """
    categories_text = ", ".join(categories) if categories and len(categories) > 0 else "any"
    
    final_prompt = template.replace("__description__", text)
    if "{__categories__}" in final_prompt:
        final_prompt = final_prompt.replace("{__categories__}", categories_text)
    
    return final_prompt
