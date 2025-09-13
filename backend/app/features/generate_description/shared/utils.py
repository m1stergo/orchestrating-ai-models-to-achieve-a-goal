"""
Utility functions for generate_description module.
"""
import re
import json
import logging
from typing import Optional


logger = logging.getLogger(__name__)

"""
Shared prompt templates for text generation adapters.
"""
def get_product_description_prompt(custom_prompt: str = None, product_description: str = None, categories: list = None) -> str:
    """
    Get the product description prompt template.
    
    Args:
        custom_prompt: Optional custom prompt to use instead of default
        
    Returns:
        str: The prompt template with placeholders
    """
    base_instruction = custom_prompt if custom_prompt and custom_prompt.strip() else """
    You are a professional e-commerce copywriter.
    Write a short, concise product description for ecommerce page.

    Rules:
    - Title must be concise, clear, and descriptive (max 10 words)
    - Description must be direct, simple, and factual (40-60 words max)
    - Use short sentences, avoid marketing fluff and adjectives like "elevate", "charming", "whimsy"
    - Focus on features first, then benefits
    - Keywords must not repeat, must be relevant for SEO
    """

    base_instruction = base_instruction + "\n\n" + "Product: " + product_description

    categories_text = ", ".join(categories) if categories and len(categories) > 0 else "any"
    
    json_structure = """Return a valid JSON response with the following structure:
    {
    "title": "Inferred product title/name",
    "description": "product description",
    "keywords": ["5 relevant SEO keywords, 1-3 words each, lowercase"],
    "category": "Suggested product category from this list: [categories]"
    }""".replace("[categories]", categories_text)

    return base_instruction + "\n\n" + json_structure


def get_promotional_audio_script_prompt(custom_prompt: Optional[str] = None, text: str = None) -> str:
    """
    Get promotional audio script prompt template.
    
    Args:
        custom_prompt: Optional custom prompt from user settings
        
    Returns:
        str: The prompt template
    """
    base_instruction = custom_prompt if custom_prompt and custom_prompt.strip() else """
    Create a short description for a Reels/TikTok promotional video.
    The result should sound natural, conversational, and energetic, with short, punchy sentences that grab attention in the first few seconds.
    Include a strong hook at the beginning, a simple middle part, and a call-to-action at the end.
    Avoid being too formal, use common social media expressions, and keep the length suitable for a video under 30 seconds.
    Do not use emojis!
    """

    json_structure = """Return a valid JSON response with the following structure:
    {
    "description": "Inferred product description",
    }"""
    
    return base_instruction + "\n\n" + "Product: " + text + "\n\n" + json_structure


def extract_json_from_response(response_text: str) -> str:
    """
    Extract JSON from response text that may contain markdown code blocks.
    
    Args:
        response_text: Text response from an AI model that might contain JSON
        
    Returns:
        Extracted and validated JSON string or original text if no valid JSON found
    """
    if not response_text:
        return response_text
        
    # Try to find JSON within markdown code blocks
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1).strip()
        try:
            # Validate it's proper JSON by parsing and re-serializing
            parsed = json.loads(json_str)
            return json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError:
            logger.warning("Found JSON block but couldn't parse it, returning original")
            return response_text
    
    # If no code blocks, try to find JSON directly
    try:
        # Look for JSON object pattern
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            parsed = json.loads(json_str)
            return json.dumps(parsed, ensure_ascii=False)
    except json.JSONDecodeError:
        pass
        
    # Return original if no valid JSON found
    return response_text
