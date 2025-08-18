"""
OpenAI adapter for image description.
"""
import logging
import asyncio
import base64
import aiofiles
from typing import Optional
from urllib.parse import urlparse
from pathlib import Path
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
            # Always convert to base64 for better reliability
            image_data = await self._convert_image_to_base64(image_url)
            result_text = await asyncio.to_thread(self.describe_image_sync, image_data, prompt)
            
            logger.info("OpenAI model described image successfully")
            return result_text
        except Exception as e:
            logger.error(f"OpenAI image description error: {e}")
            raise

    async def _convert_image_to_base64(self, image_url: str) -> str:
        """Convert an image URL to base64 data URL."""
        try:
            # Extract the local file path from the URL
            parsed = urlparse(image_url)
            # Remove the leading slash and convert to local path
            relative_path = parsed.path.lstrip('/')
            
            # Construct the full path (assuming static files are served from app/static)
            base_path = Path(__file__).parent.parent.parent  # Go up to app/
            file_path = base_path / relative_path
            
            logger.info(f"Reading image file: {file_path}")
            
            # Read the file asynchronously
            async with aiofiles.open(file_path, 'rb') as f:
                image_data = await f.read()
            
            # Encode to base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # Determine MIME type based on file extension
            extension = file_path.suffix.lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg', 
                '.png': 'image/png',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }.get(extension, 'image/jpeg')
            
            return f"data:{mime_type};base64,{base64_data}"
            
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            raise ValueError(f"Could not read image file: {e}")

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
