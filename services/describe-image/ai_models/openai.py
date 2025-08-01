import httpx
import logging
from urllib.parse import urlparse

from schemas import DescribeImageResponse  # Asegurate que la ruta esté bien
from .base import ImageDescriptionModel
from config import settings

logger = logging.getLogger(__name__)


class OpenAIVisionModel(ImageDescriptionModel):
    """Model for image description using OpenAI GPT-4 Vision API."""

    def __init__(self):
        super().__init__()
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
        self.model = settings.OPENAI_MODEL

    def is_available(self) -> bool:
        """Check if OpenAI API key is configured."""
        available = bool(self.api_key and self.api_key.strip())
        if not available:
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        return available

    def is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme in ("http", "https"), result.netloc])
        except Exception:
            return False

    async def describe_image(self, image_url: str, prompt: str = None) -> DescribeImageResponse:
        """Describe image using OpenAI GPT-4 Vision API."""
        logger.info(f"describing image from {image_url}")

        if not self.is_available():
            raise ValueError("OpenAI API key is not configured. Set OPENAI_API_KEY environment variable.")

        if not self.is_valid_url(image_url):
            raise ValueError("Invalid image URL")

        # Default prompt: load from file if not provided
        if prompt is None:
            from pathlib import Path
            PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "default.txt"
            prompt = PROMPT_PATH.read_text(encoding="utf-8")

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

                logger.info("OpenAIVisionModel: description generated successfully")
                return DescribeImageResponse(description=description)

        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"OpenAI API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"OpenAIVisionModel error: {str(e)}")
            raise
