"""
OpenAI adapter for text generation and image description.
"""
import logging
import asyncio
from typing import Optional

from openai import OpenAI
from app.config import settings
from .base import TextGenerationAdapter, ImageDescriptionAdapter, PROMOTIONAL_AUDIO_SCRIPT_PROMPT

logger = logging.getLogger(__name__)


class OpenAIAdapter(TextGenerationAdapter, ImageDescriptionAdapter):
    """OpenAI adapter for both text generation and image description."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = settings.OPENAI_TEXT_MODEL  # e.g., "gpt-4o-mini"
        self.model = None

        if self.is_available():
            self.model = OpenAI(api_key=self.api_key)

    def is_available(self) -> bool:
        """Check if the OpenAI API key is available."""
        available = bool(self.api_key and self.api_key.strip())
        if not available:
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        return available

    async def generate_text(self, text: str, prompt: str) -> str:
        """Generate text using OpenAI's text model."""
        if not self.is_available():
            raise ValueError("OpenAI API key is not configured.")

        # Use structured JSON prompt for product description
        json_prompt = """Based on the provided text, create a comprehensive product description and return a JSON response with the following structure:
{
  "title": "Inferred product title/name",
  "description": "Detailed product description",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "category": "Suggested product category"
}

Please ensure:
- The title is concise and descriptive
- The description is detailed and highlights key features
- Keywords are relevant for search and marketing
- Category is a general product classification from this list: [clothing, electronics, health, home, jewelry, sports, toys]
- Response must be valid JSON only, no additional text"""

        full_prompt = f"{json_prompt}\n\nText to process:\n{text}"

        try:
            result_text = await asyncio.to_thread(self.generate_text_sync, full_prompt)
            logger.info("OpenAI model generated text successfully")
            return result_text
        except Exception as e:
            logger.error(f"OpenAI text generation error: {e}")
            raise

    async def generate_promotional_audio_script(self, text: str) -> str:
        """Generate a promotional audio script using OpenAI's text model."""
        if not self.is_available():
            raise ValueError("OpenAI API key is not configured.")

        full_prompt = f"{PROMOTIONAL_AUDIO_SCRIPT_PROMPT}\n\nOriginal text:\n{text}"

        try:
            result_text = await asyncio.to_thread(self.generate_promotional_audio_script_sync, full_prompt)
            logger.info("OpenAI model generated promotional audio script successfully")
            return result_text
        except Exception as e:
            logger.error(f"OpenAI promotional audio script generation error: {e}")
            raise

    async def describe_image(self, image_url: str, prompt: Optional[str] = None) -> str:
        """Describe an image using OpenAI's vision model."""
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

    def generate_text_sync(self, full_prompt: str) -> str:
        """Synchronous method to generate text using OpenAI."""
        if self.model is None:
            self.model = OpenAI(api_key=self.api_key)

        resp = self.model.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=1000,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        text = resp.choices[0].message.content or ""
        return text.strip()

    def generate_promotional_audio_script_sync(self, full_prompt: str) -> str:
        """Synchronous method to generate promotional audio script using OpenAI without JSON format."""
        if self.model is None:
            self.model = OpenAI(api_key=self.api_key)

        resp = self.model.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=500,
            temperature=0.7,
        )
        text = resp.choices[0].message.content or ""
        return text.strip()