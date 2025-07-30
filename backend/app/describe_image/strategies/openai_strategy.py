import os
import httpx
from app.describe_image.schemas import DescribeImageResponse
from .base import ImageDescriptionStrategy
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class OpenAIVisionStrategy(ImageDescriptionStrategy):
    """Strategy for image description using OpenAI GPT-4 Vision API."""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-4-vision-preview"
    
    def is_available(self) -> bool:
        """Check if OpenAI API key is configured."""
        return self.api_key is not None and len(self.api_key.strip()) > 0

    def is_valid_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    async def describe_image(self, image_url: str, **kwargs) -> DescribeImageResponse:
        """Describe image using OpenAI GPT-4 Vision API."""
        logger.info(f"🚀 OpenAIVisionStrategy: describing image from {image_url}")
        
        if not self.is_available():
            raise ValueError("OpenAI API key is not configured. Set OPENAI_API_KEY environment variable.")
        
        if not self.is_valid_url(image_url):
            raise ValueError("Invalid image URL")
        
        try:
            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze the main product in this image. Focus only on the product itself.

Then complete the following template with what you can observe from the image. If a field cannot be determined from the image alone, say "Not visible" or "Unknown".

Here is the product information:

Image description: {Insert a short but complete visual description of the item, including color, shape, material, and texture}
Product type: {What is the object?}
Material: {What is it made of?}
Keywords: {List relevant keywords that describe the item visually or functionally}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1
            }
            
            # Make the API request
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
