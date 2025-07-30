import os
import httpx
import logging
import base64
from urllib.parse import urlparse
from typing import Dict, Any

from schemas import DescribeImageResponse
from .base import ImageDescriptionStrategy

logger = logging.getLogger(__name__)


class GeminiStrategy(ImageDescriptionStrategy):
    """Strategy for image description using Google Gemini Pro Vision API."""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        # self.model = "gemini-1.5-flash"
        self.model = "gemini-2.5-pro"

    def is_available(self) -> bool:
        """Check if Gemini API key is configured."""
        available = bool(self.api_key and self.api_key.strip())
        logger.info(f"🔍 Gemini Strategy availability check: {available}")
        if not available:
            logger.warning("⚠️ Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        else:
            logger.info(f"✅ Gemini API key configured (length: {len(self.api_key)})")
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
            logger.error(f"❌ Error downloading image: {str(e)}")
            raise

    async def describe_image(self, image_url: str, prompt: str = None, **kwargs) -> DescribeImageResponse:
        """Describe image using Google Gemini Pro Vision API."""
        logger.info(f"🚀 GeminiStrategy: describing image from {image_url}")

        if not self.is_available():
            raise ValueError("Gemini API key is not configured. Set GEMINI_API_KEY environment variable.")

        if not self.is_valid_url(image_url):
            raise ValueError("Invalid image URL")

        # Default prompt (same as your script)
        prompt = prompt or """Analyze the main product in the image provided. Focus exclusively on the product itself. Based on your visual analysis of the product, complete the following template. If any field cannot be determined from the image, state "Not visible" or "Unknown".

Image description: A brief but comprehensive visual description of the item, detailing its color, shape, material, and texture.
Product type: What is the object?
Material: What is it made of? Be specific if possible (e.g., "leather," "plastic," "wood").
Keywords: List relevant keywords that describe the item's appearance or function."""

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

            # Make the API request
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{self.model}:generateContent",
                    json=payload,
                    params={"key": self.api_key}
                )
                response.raise_for_status()
                result = response.json()

                # Extract the generated text
                description = self._extract_description(result)
                
                logger.info("✅ GeminiStrategy: description generated successfully")
                return DescribeImageResponse(description=description)

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Gemini API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Gemini API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"❌ GeminiStrategy error: {str(e)}")
            raise

    def _extract_description(self, result: Dict[str, Any]) -> str:
        """Extract description from Gemini API response."""
        try:
            candidates = result.get("candidates", [])
            if not candidates:
                return "No description generated"

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            
            if not parts:
                return "No description generated"

            description = parts[0].get("text", "No description generated")
            return description.strip()

        except Exception as e:
            logger.error(f"❌ Error extracting description: {str(e)}")
            return f"Error processing response: {str(e)}"
