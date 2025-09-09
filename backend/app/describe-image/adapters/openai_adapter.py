"""
OpenAI adapter for image description.
"""
import logging
from typing import Optional
from openai import OpenAI
from app.config import settings
from .base import ImageDescriptionAdapter
from ..shared.prompts import get_image_description_prompt
from .utils import convert_image_to_base64

logger = logging.getLogger(__name__)


class OpenAIAdapter(ImageDescriptionAdapter):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = settings.OPENAI_VISION_MODEL  # e.g., "gpt-4o"
        self.model = None

        if self.is_available():
            self.model = OpenAI(api_key=self.api_key)
    
    def is_available(self) -> bool:
        """Check if the OpenAI API key is available."""
        available = bool(self.api_key and self.api_key.strip())
        if not available:
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        return available

    async def describe_image(self, image_url: str, prompt: Optional[str] = None) -> str:
        """Describe an image using OpenAI's vision model."""
        logger.info(f"OpenAI: describing image from {image_url}")

        if not self.is_available():
            raise ValueError("OpenAI API key is not configured.")

        final_prompt = get_image_description_prompt(prompt)

        try:
            image_data = await convert_image_to_base64(image_url)
            result_text = self.describe_image_sync(image_data, final_prompt)
            
            logger.info("OpenAI model described image successfully")
            return result_text
        except Exception as e:
            logger.error(f"OpenAI image description error: {e}")
            raise

    def describe_image_sync(self, image_data: str, prompt: str) -> str:
        """Describe image using base64 data."""
        if self.model is None:
            self.model = OpenAI(api_key=self.api_key)
            
        result = self.model.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data}}
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.7,
        )

        return result.choices[0].message.content or ""

    async def warmup(self) -> str:
        """
        Warmup the OpenAI adapter.
        
        Returns:
            str with warmup status and information
        """
        if not self.is_available():
            raise ValueError("OpenAI API key is not configured.")
            
        logger.info("OpenAI warmup successful")
        return "OpenAI adapter is ready"