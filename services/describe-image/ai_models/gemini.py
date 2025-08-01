import httpx
import logging
import base64
from urllib.parse import urlparse
from typing import Dict, Any

from schemas import DescribeImageResponse
from .base import ImageDescriptionModel
from config import settings

logger = logging.getLogger(__name__)

class GeminiModel(ImageDescriptionModel):
    """Model for image description using Google Vision API."""

    def __init__(self):
        super().__init__()
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = settings.GEMINI_MODEL

    def is_available(self) -> bool:
        """Check if Gemini API key is configured."""
        available = bool(self.api_key and self.api_key.strip())
        if not available:
            logger.warning("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        return available

    def is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme in ("http", "https"), result.netloc])
        except Exception:
            return False

    async def _download_image_as_base64(self, image_url: str) -> str:
        """Download image from URL and convert to base64."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_data = response.content
                return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            raise

    async def describe_image(self, image_url: str, prompt: str = None, **kwargs) -> DescribeImageResponse:
        """Describe image using Google Gemini Pro Vision API."""
        logger.info(f"GeminiModel: describing image from {image_url}")

        if not self.is_available():
            raise ValueError("Gemini API key is not configured. Set GEMINI_API_KEY environment variable.")

        if not self.is_valid_url(image_url):
            raise ValueError("Invalid image URL")

        # Default prompt: load from file if not provided
        if prompt is None:
            from pathlib import Path
            PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "default.txt"
            prompt = PROMPT_PATH.read_text(encoding="utf-8")

        try:
            # Download and encode image
            base64_image = await self._download_image_as_base64(image_url)

            # Prepare the request payload for Gemini API
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            },
                            {
                                "inlineData": {
                                    "mimeType": "image/jpeg",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{self.model}:generateContent",
                    json=payload,
                    params={"key": self.api_key}
                )
                response.raise_for_status()
                result = response.json()

                # Extract the generated text
                description = self._parse_response(result)
                
                logger.info("GeminiModel: description generated successfully")
                return DescribeImageResponse(description=description)

        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Gemini API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"GeminiModel error: {str(e)}")
            raise

    def _parse_response(self, result: Dict[str, Any]) -> str:
        """Parse response from Gemini API response."""
        try:
            candidates = result.get("candidates", [])
            if not candidates:
                return "No response generated"

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            
            if not parts:
                return "No response generated"

            output = parts[0].get("text", "No response generated")
            return output.strip()

        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return f"Error processing response: {str(e)}"

