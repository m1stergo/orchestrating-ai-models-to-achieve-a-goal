"""
Mistral adapter for text generation
"""
import logging
import aiohttp
from app.config import settings
from .base import TextGenerationAdapter, ECOMMERCE_COPYWRITER_PROMPT, REEL_PROMOTIONAL_PROMPT

logger = logging.getLogger(__name__)


class MistralAdapter(TextGenerationAdapter):
    def __init__(self):
        self.service_url = settings.MISTRAL_SERVICE_URL
        self.timeout = aiohttp.ClientTimeout(total=60)  # 60 seconds timeout for inference

    def is_available(self) -> bool:
        """Check if the Mistral service URL is available."""
        available = bool(self.service_url and self.service_url.strip())
        if not available:
            logger.warning("Mistral service URL not found. Set MISTRAL_SERVICE_URL environment variable.")
        return available

    async def generate_text(self, text: str, prompt: str) -> str:
        """Generate text using the Mistral model microservice."""
        if not self.is_available():
            raise ValueError("Mistral service URL is not configured.")

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # First check if the service is healthy
                try:
                    health_url = f"{self.service_url}/healthz"
                    async with session.get(health_url) as health_resp:
                        health_data = await health_resp.json()
                        if not health_resp.ok or not health_data.get("loaded", False):
                            logger.error(f"Mistral service not ready: {health_resp.status}")
                            return "Service not available. The model is still loading or not responding."
                except Exception as e:
                    logger.error(f"Failed to check Mistral service health: {str(e)}")
                    return "Service health check failed. The service may be down."

                # Call the generate-text endpoint
                payload = {
                    "text": text,
                    "prompt": ECOMMERCE_COPYWRITER_PROMPT  # Use shared e-commerce copywriter prompt
                }
                
                async with session.post(f"{self.service_url}/generate-text", json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Mistral service error: {resp.status}, {error_text}")
                        return f"Service error: {resp.status}"
                    
                    result = await resp.json()
                    description = result.get("text", "")
                    logger.info("Mistral service generated text successfully")
                    return description

        except aiohttp.ClientError as e:
            logger.error(f"Mistral service connection error: {str(e)}")
            return f"Service connection error: {str(e)}"
        except Exception as e:
            logger.error(f"Mistral adapter error: {str(e)}")
            raise

    async def generate_reel_script(self, text: str) -> str:
        """Generate a promotional reel script using the Mistral model microservice."""
        if not self.is_available():
            raise ValueError("Mistral service URL is not configured.")

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # First check if the service is healthy
                try:
                    health_url = f"{self.service_url}/healthz"
                    async with session.get(health_url) as health_resp:
                        health_data = await health_resp.json()
                        if not health_resp.ok or not health_data.get("loaded", False):
                            logger.error(f"Mistral service not ready: {health_resp.status}")
                            return "Service not available. The model is still loading or not responding."
                except Exception as e:
                    logger.error(f"Failed to check Mistral service health: {str(e)}")
                    return "Service health check failed. The service may be down."

                # Call the generate-text endpoint with reel prompt
                payload = {
                    "text": text,
                    "prompt": REEL_PROMOTIONAL_PROMPT  # Use reel promotional prompt
                }
                
                async with session.post(f"{self.service_url}/generate-text", json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Mistral service error: {resp.status}, {error_text}")
                        return f"Service error: {resp.status}"
                    
                    result = await resp.json()
                    script = result.get("text", "")
                    logger.info("Mistral service generated reel script successfully")
                    return script

        except aiohttp.ClientError as e:
            logger.error(f"Mistral service connection error: {str(e)}")
            return f"Service connection error: {str(e)}"
        except Exception as e:
            logger.error(f"Mistral reel script generation error: {str(e)}")
            raise
