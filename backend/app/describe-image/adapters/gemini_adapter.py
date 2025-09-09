"""
Gemini adapter for image description.
"""
import logging
import asyncio
from typing import Optional
import google.generativeai as genai

from app.config import settings
from .base import ImageDescriptionAdapter
from ..shared.prompts import get_image_description_prompt

logger = logging.getLogger(__name__)


class GeminiAdapter(ImageDescriptionAdapter):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_VISION_MODEL  # e.g., "gemini-1.5-pro-vision-latest"
        self.model = None

        if self.is_available():
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
    

    def is_available(self) -> bool:
        """Check if the Gemini API key is available."""
        available = bool(self.api_key and self.api_key.strip())
        if not available:
            logger.warning("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        return available

    async def describe_image(self, image_url: str, prompt: Optional[str] = None) -> str:
        """Describe an image using Gemini's vision model."""
        logger.info(f"Gemini: describing image from {image_url}")

        if not self.is_available():
            raise ValueError("Gemini API key is not configured.")

        # Use custom prompt or default
        final_prompt = get_image_description_prompt(prompt)

        try:
            result_text = await asyncio.to_thread(self.describe_image_sync, image_url, final_prompt)
            logger.info("Gemini model described image successfully")
            return result_text
        except Exception as e:
            logger.error(f"Gemini image description error: {e}")
            raise

    def describe_image_sync(self, image_url: str, prompt: str) -> str:
        # For Gemini, we need to download the image and pass it as inline data
        import requests
        import base64
        
        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Convert to base64
        image_data = base64.b64encode(response.content).decode('utf-8')
        
        result = self.model.generate_content(
            [
                prompt,
                {"mime_type": "image/jpeg", "data": image_data}
            ],
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 500,
            },
        )

        return result.text

    async def warmup(self) -> dict:
        """
        Warmup the Gemini adapter.
        
        Returns:
            Dict with warmup status and information
        """
        if not self.is_available():
            return {
                "status": "error",
                "message": "Gemini API key is not configured",
            }
        
        logger.info("Gemini warmup successful")
        return {
            "status": "success",
            "message": "Gemini adapter is ready",
        }
