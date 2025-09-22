"""
Utility functions for the generate_description module.

This module provides helper functions for generating product descriptions
and promotional audio scripts, including prompt templates and JSON response
parsing. It supports customizable prompts from user settings with fallback
to default templates.

Functions:
    get_product_description_prompt: Generate a prompt for product descriptions
    get_promotional_audio_script_prompt: Generate a prompt for audio scripts
    extract_json_from_response: Parse JSON from AI model responses
"""
import re
import json
import logging
from typing import Optional, List

# Configure module logger
logger = logging.getLogger(__name__)

# Prompt templates for text generation with AI models
def get_product_description_prompt(custom_prompt: Optional[str] = None, categories: Optional[List[str]] = None) -> str:
    """
    Get the product description prompt template for AI models.
    
    This function generates a prompt for AI models to create product descriptions.
    It can use either a custom prompt from user settings or a default template.
    The prompt includes instructions for format, style, and a JSON structure for
    the expected response.
    
    Args:
        custom_prompt: Optional custom prompt from user settings
        categories: Optional list of valid product categories to choose from
        
    Returns:
        str: The complete prompt template to send to the AI model
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
    categories_text = ", ".join(categories) if categories and len(categories) > 0 else "any"
    
    json_structure = """Return a valid JSON response with the following structure:
    {
    "title": "Inferred product title/name",
    "description": "product description",
    "keywords": ["5 relevant SEO keywords, 1-3 words each, lowercase"],
    "category": "Suggested product category from this list: [categories]"
    }""".replace("[categories]", categories_text)

    return base_instruction + "\n\n" + json_structure


def get_promotional_audio_script_prompt(custom_prompt: Optional[str] = None) -> str:
    """
    Get promotional audio script prompt template for AI models.
    
    This function generates a prompt for AI models to create short, engaging
    audio scripts for product promotions suitable for social media platforms.
    It can use either a custom prompt from user settings or a default template.
    
    Args:
        custom_prompt: Optional custom prompt from user settings
        
    Returns:
        str: The complete prompt template to send to the AI model
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
    "description": "Promotional video script",
    }"""
    
    return base_instruction + "\n\n" + json_structure


def extract_json_from_response(response_text: str) -> str:
    """
    Extract JSON from response text that may contain markdown code blocks.
    
    This function parses responses from AI models to extract valid JSON data.
    It handles various formats including markdown code blocks and directly
    embedded JSON objects. If valid JSON is found, it's validated and
    normalized before returning.
    
    Args:
        response_text: Text response from an AI model that might contain JSON
        
    Returns:
        str: Extracted and validated JSON string, or the original text if no valid JSON found
        
    Note:
        The function tries multiple extraction methods:
        1. Finding JSON in markdown code blocks (```json ... ```)
        2. Looking for JSON objects directly in the text ({...})
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
