"""
OpenAI adapter for image description.
"""
import logging
import asyncio
from typing import Optional
from openai import OpenAI
from app.config import settings
from .base import ImageDescriptionAdapter

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

        if prompt is None:
            prompt = "Describe this image in detail."

        try:
            result_text = await asyncio.to_thread(self.describe_image_sync, image_url, prompt)
            logger.info("OpenAI model described image successfully")
            return result_text
        except Exception as e:
            logger.error(f"OpenAI image description error: {e}")
            raise


    def describe_image_sync(self, image_url: str, prompt: str) -> str:
        if self.model is None:
            # Fallback si el modelo no se inicializó en el constructor
            self.model = OpenAI(api_key=self.api_key)
            
        result = self.model.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.7,
        )

        return result.choices[0].message.content or ""
