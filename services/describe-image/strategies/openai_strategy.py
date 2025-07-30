import os
import httpx
import logging
from urllib.parse import urlparse

from schemas import DescribeImageResponse  # Asegurate que la ruta esté bien
from .base import ImageDescriptionStrategy

logger = logging.getLogger(__name__)


class OpenAIVisionStrategy(ImageDescriptionStrategy):
    """Strategy for image description using OpenAI GPT-4 Vision API."""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-4o"

    def is_available(self) -> bool:
        """Check if OpenAI API key is configured."""
        available = bool(self.api_key and self.api_key.strip())
        logger.info(f"🔍 OpenAI Strategy availability check: {available}")
        if not available:
            logger.warning("⚠️ OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        else:
            logger.info(f"✅ OpenAI API key configured (length: {len(self.api_key)})")
        return available

    def is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme in ("http", "https"), result.netloc])
        except Exception:
            return False

    async def describe_image(self, image_url: str, prompt: str = None, **kwargs) -> DescribeImageResponse:
        """Describe image using OpenAI GPT-4 Vision API."""
        logger.info(f"🚀 OpenAIVisionStrategy: describing image from {image_url}")

        if not self.is_available():
            raise ValueError("OpenAI API key is not configured. Set OPENAI_API_KEY environment variable.")

        if not self.is_valid_url(image_url):
            raise ValueError("Invalid image URL")

        # Default prompt (puede ser reemplazado vía argumento)
        prompt = prompt or """Analyze the main product in this image. Focus only on the product itself.

Then complete the following template with what you can observe from the image. If a field cannot be determined from the image alone, say "Not visible" or "Unknown".

Here is the product information:

Image description: {Insert a short but complete visual description of the item, including color, shape, material, and texture}
Product type: {What is the object?}
Material: {What is it made of?}
Keywords: {List relevant keywords that describe the item visually or functionally}"""

        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}}
                        ]
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                description = result["choices"][0]["message"]["content"]

                logger.info("✅ OpenAIVisionStrategy: description generated successfully")
                return DescribeImageResponse(description=description)

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ OpenAI API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"OpenAI API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"❌ OpenAIVisionStrategy error: {str(e)}")
            raise
