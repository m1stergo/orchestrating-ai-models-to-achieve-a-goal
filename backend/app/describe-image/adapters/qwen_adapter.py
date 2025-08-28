"""
Qwen adapter for image description
"""
import logging
import aiohttp
from typing import Optional

from app.config import settings
from .base import ImageDescriptionAdapter

logger = logging.getLogger(__name__)


class QwenAdapter(ImageDescriptionAdapter):
    def __init__(self):
        self.service_url = settings.DESCRIBE_IMAGE_QWEN_URL
        self.timeout = aiohttp.ClientTimeout(total=60)  # 60 seconds timeout for inference
    
    def _get_image_description_prompt(self, custom_prompt: Optional[str] = None) -> str:
        """Get image description prompt template."""
        if custom_prompt and custom_prompt.strip():
            return custom_prompt
            
        return """Analyze the main product in the image provided. Focus exclusively on the product itself. Based on your visual analysis of the product, complete the following template. If any field cannot be determined from the image, state "Not visible" or "Unknown".

Image description: A brief but comprehensive visual description of the item, detailing its color, shape, material, and texture.
Product type: What is the object?
Material: What is it made of? Be specific if possible (e.g., "leather," "plastic," "wood").
Keywords: List relevant keywords that describe the item's appearance or function."""

    def is_available(self) -> bool:
        """Check if the Qwen service URL is available."""
        available = bool(self.service_url and self.service_url.strip())
        if not available:
            logger.warning("Qwen service URL not found. Set DESCRIBE_IMAGE_QWEN_URL environment variable.")
        return available

    async def describe_image(self, image_url: str, prompt: Optional[str] = None) -> str:
        """Describe an image using the Qwen VL model microservice."""
        if not self.is_available():
            raise ValueError("Qwen service URL is not configured.")

        # Use custom prompt or default
        final_prompt = self._get_image_description_prompt(prompt)

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # First check if the service is healthy
                try:
                    health_url = f"{self.service_url}/healthz"
                    async with session.get(health_url) as health_resp:
                        if not health_resp.ok:
                            logger.error(f"Qwen service health check failed: {health_resp.status}")
                            return "Service not available. Health check failed."
                        
                        health_data = await health_resp.json()
                        if not health_data.get("loaded", False):
                            logger.info(f"Qwen service model not loaded yet: {health_data}")
                            # Return a specific error that the frontend can catch
                            raise Exception("QWEN_NOT_READY: The model is still loading. Please try the warmup endpoint first.")
                except Exception as e:
                    logger.error(f"Failed to check Qwen service health: {str(e)}")
                    # If it's a connection error, the service is likely not running (cold start)
                    raise Exception("QWEN_SERVICE_DOWN: Service health check failed. The service may be down or starting up.")

                # Call the describe-image endpoint
                payload = {
                    "image_url": image_url,
                    "prompt": final_prompt
                }
                
                async with session.post(f"{self.service_url}/describe-image", json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Qwen service error: {resp.status}, {error_text}")
                        return f"Service error: {resp.status}"
                    
                    result = await resp.json()
                    description = result.get("description", "")
                    logger.info("Qwen service described image successfully")
                    return description

        except aiohttp.ClientError as e:
            logger.error(f"Qwen service connection error: {str(e)}")
            return f"Service connection error: {str(e)}"
        except Exception as e:
            logger.error(f"Qwen adapter error: {str(e)}")
            raise
