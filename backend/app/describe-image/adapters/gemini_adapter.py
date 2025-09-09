import logging
import asyncio
from typing import Optional
import google.generativeai as genai

from app.config import settings
from .base import ImageDescriptionAdapter
from ..shared.prompts import get_image_description_prompt
from .utils import convert_image_to_base64

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
            # Convertir imagen a base64
            image_data_url = await convert_image_to_base64(image_url)
            
            # Ejecutar la generación en un thread separado ya que es una operación sincrónica
            result_text = await asyncio.to_thread(
                self.describe_image_sync, image_data_url, final_prompt
            )
            
            logger.info("Gemini model described image successfully")
            return result_text
        except Exception as e:
            logger.error(f"Gemini image description error: {e}")
            raise

    def describe_image_sync(self, image_data_url: str, prompt: str) -> str:
        # Extract only the base64 part from the data URL (remove the mime type prefix)
        if ',' in image_data_url:
            image_data = image_data_url.split(',', 1)[1]
        else:
            image_data = image_data_url
        
        result = self.model.generate_content(
            [
                prompt,
                {"mime_type": "image/jpeg", "data": image_data}
            ],
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1000,
            },
        )

        return result.text

    async def warmup(self) -> str:
        """
        Warmup the Gemini adapter.
        
        Returns:
            str with warmup status and information
        """
        if not self.is_available():
            raise ValueError("Gemini API key is not configured.")
            
        logger.info("Gemini warmup successful")
        return "Gemini adapter is ready"
