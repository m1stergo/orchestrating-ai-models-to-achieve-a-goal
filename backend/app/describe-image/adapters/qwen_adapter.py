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
        self.service_url = settings.QWEN_SERVICE_URL
        self.timeout = aiohttp.ClientTimeout(total=60)  # 60 seconds timeout for inference

    def is_available(self) -> bool:
        """Check if the Qwen service URL is available."""
        available = bool(self.service_url and self.service_url.strip())
        if not available:
            logger.warning("Qwen service URL not found. Set QWEN_SERVICE_URL environment variable.")
        return available

    async def describe_image(self, image_url: str, prompt: Optional[str] = None) -> str:
        """Describe an image using the Qwen VL model microservice."""
        if not self.is_available():
            raise ValueError("Qwen service URL is not configured.")

        if prompt is None:
            prompt = "Describe this image in detail."

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # First check if the service is healthy
                try:
                    health_url = f"{self.service_url}/healthz"
                    async with session.get(health_url) as health_resp:
                        health_data = await health_resp.json()
                        if not health_resp.ok or not health_data.get("loaded", False):
                            logger.error(f"Qwen service not ready: {health_resp.status}")
                            return "Service not available. The model is still loading or not responding."
                except Exception as e:
                    logger.error(f"Failed to check Qwen service health: {str(e)}")
                    return "Service health check failed. The service may be down."

                # Call the describe-image endpoint
                payload = {
                    "image_url": image_url,
                    "prompt": prompt
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
