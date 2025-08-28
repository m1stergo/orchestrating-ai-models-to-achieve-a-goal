"""
Mistral adapter for text generation
"""
import logging
import aiohttp
from typing import Optional, List
from app.config import settings
from .base import TextGenerationAdapter

logger = logging.getLogger(__name__)


class MistralAdapter(TextGenerationAdapter):
    def __init__(self):
        self.service_url = settings.MISTRAL_SERVICE_URL
        self.timeout = aiohttp.ClientTimeout(total=60)  # 60 seconds timeout for inference
    
    def _get_product_description_prompt(self, custom_prompt: Optional[str] = None, product_description: str = None, categories: list = None) -> str:
        """Get product description prompt template."""
        base_instruction = custom_prompt if custom_prompt and custom_prompt.strip() else """
        You are a professional e-commerce copywriter.
        Write a short, concise product description for ecommerce page.

        Rules:
        - Title must be concise, clear, and descriptive (max 10 words)
        - Description must be direct, simple, and factual (40-60 words max)
        - Use short sentences, avoid marketing fluff and adjectives like "elevate", "charming", "whimsy"
        - Focus on features first, then benefits
        - Keywords must not repeat, must be relevant for SEO
        """

        base_instruction = base_instruction + "\n\n" + "Product: " + product_description

        categories_text = ", ".join(categories) if categories and len(categories) > 0 else "any"
    
        json_structure = """Return a valid JSON response with the following structure:
        {
        "title": "Inferred product title/name",
        "description": "product description",
        "keywords": ["5 relevant SEO keywords, 1-3 words each, lowercase"],
        "category": "Suggested product category from this list: [categories]"
        }""".replace("[categories]", categories_text)

        return base_instruction + "\n\n" + json_structure
    
    def _get_promotional_audio_script_prompt(self, custom_prompt: Optional[str] = None, text: str = None) -> str:
        """Get promotional audio script prompt template."""
        base_instruction = custom_prompt if custom_prompt and custom_prompt.strip() else """
        Create a short description for a Reels/TikTok promotional video.
        The result should sound natural, conversational, and energetic, with short, punchy sentences that grab attention in the first few seconds.
        Include a strong hook at the beginning, a simple middle part, and a call-to-action at the end.
        Avoid being too formal, use common social media expressions, and keep the length suitable for a video under 30 seconds.
        Do not use emojis!
        """
        return base_instruction + "\n\n" + "Product: " + text

    def is_available(self) -> bool:
        """Check if the Mistral service URL is available."""
        available = bool(self.service_url and self.service_url.strip())
        if not available:
            logger.warning("Mistral service URL not found. Set MISTRAL_SERVICE_URL environment variable.")
        return available

    async def generate_text(self, text: str, prompt: Optional[str] = None, categories: Optional[List[str]] = None) -> str:
        """Generate text using the Mistral model microservice."""
        if not self.is_available():
            raise ValueError("Mistral service URL is not configured.")

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # First check if the service is healthy
                health_url = f"{self.service_url}/healthz"
                async with session.get(health_url) as health_resp:
                    if not health_resp.ok:
                        logger.error(f"Mistral service health check failed: {health_resp.status}")
                        raise Exception("MISTRAL_SERVICE_DOWN: Service health check failed. The service may be down or starting up.")
                    
                    health_data = await health_resp.json()
                    if not health_data.get("loaded", False):
                        logger.info(f"Mistral service model not loaded yet: {health_data}")
                        # Return a specific error that the frontend can catch
                        raise Exception("MISTRAL_NOT_READY: The model is still loading. Please try the warmup endpoint first.")

                # Call the generate-text endpoint
                full_prompt = self._get_product_description_prompt(prompt, text, categories)
                
                payload = {
                    "text": text,
                    "prompt": full_prompt
                }
                
                async with session.post(f"{self.service_url}/generate-description", json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Mistral service error: {resp.status}, {error_text}")
                        raise Exception(f"MISTRAL_SERVICE_ERROR: Service error {resp.status}")
                    
                    result = await resp.json()
                    description = result.get("text", "")
                    logger.info("Mistral service generated text successfully")
                    return description

        except aiohttp.ClientError as e:
            logger.error(f"Mistral service connection error: {str(e)}")
            raise Exception(f"MISTRAL_CONNECTION_ERROR: Service connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Mistral adapter error: {str(e)}")
            raise

    async def generate_promotional_audio_script(self, text: str, prompt: Optional[str] = None) -> str:
        """Generate a promotional audio script using the Mistral model microservice."""
        if not self.is_available():
            raise ValueError("Mistral service URL is not configured.")

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # First check if the service is healthy
                health_url = f"{self.service_url}/healthz"
                async with session.get(health_url) as health_resp:
                    if not health_resp.ok:
                        logger.error(f"Mistral service health check failed: {health_resp.status}")
                        raise Exception("MISTRAL_SERVICE_DOWN: Service health check failed. The service may be down or starting up.")
                    
                    health_data = await health_resp.json()
                    if not health_data.get("loaded", False):
                        logger.info(f"Mistral service model not loaded yet: {health_data}")
                        # Return a specific error that the frontend can catch
                        raise Exception("MISTRAL_NOT_READY: The model is still loading. Please try the warmup endpoint first.")

                # Call the generate-description endpoint with promotional audio script prompt
                full_prompt = self._get_promotional_audio_script_prompt(prompt, text)
                payload = {
                    "text": text,
                    "prompt": full_prompt
                }
                
                async with session.post(f"{self.service_url}/generate-description", json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Mistral service error: {resp.status}, {error_text}")
                        raise Exception(f"MISTRAL_SERVICE_ERROR: Service error {resp.status}")
                    
                    result = await resp.json()
                    script = result.get("text", "")
                    logger.info("Mistral service generated promotional audio script successfully")
                    return script

        except aiohttp.ClientError as e:
            logger.error(f"Mistral service connection error: {str(e)}")
            raise Exception(f"MISTRAL_CONNECTION_ERROR: Service connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Mistral promotional audio script generation error: {str(e)}")
            raise
