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
    
    def _get_product_description_prompt(self, custom_prompt: Optional[str] = None) -> str:
        """Get product description prompt template."""
        if custom_prompt and custom_prompt.strip():
            return custom_prompt
        
        return """
        You are a professional e-commerce copywriter. 
        Write a concise, benefit-focused product description for the following text:
        __description__

        Rules:
        - Title must be concise, clear, and descriptive
        - Description must be direct and persuasive (benefits before features)
        - Keywords must not repeat, must be relevant for SEO
        - Category must be chosen only from the provided list
        - Output must be valid JSON only (no markdown, no extra text)
        
        Return a JSON response with the following structure:
        {
        "title": "Inferred product title/name",
        "description": "product description highlighting key benefits and features",
        "keywords": ["5 relevant SEO keywords, 1-3 words each, lowercase"],
        "category": "Suggested product category from this list: [{__categories__}]"
        }"""
    
    def _get_promotional_audio_script_prompt(self, custom_prompt: Optional[str] = None) -> str:
        """Get promotional audio script prompt template."""
        if custom_prompt and custom_prompt.strip():
            return custom_prompt
            
        return """
        Create a short description for a Reels/TikTok promotional video.
        The result should sound natural, conversational, and energetic, with short, punchy sentences that grab attention in the first few seconds.
        Include a strong hook at the beginning, a simple middle part, and a call-to-action at the end.
        Avoid being too formal, use common social media expressions, and keep the length suitable for a video under 30 seconds.
        Do not use emojis!
        
        Transform the following text: __description__
        """
    
    def _build_final_prompt(self, prompt_template: str, text: str, categories: Optional[List[str]] = None) -> str:
        """Build final prompt by replacing placeholders."""
        final_prompt = prompt_template.replace("__description__", text)
        
        if categories and len(categories) > 0:
            categories_text = ", ".join(categories)
        else:
            categories_text = "Electronics, Clothing, Home & Garden, Sports & Outdoors, Beauty & Health, Books & Media, Toys & Games, Automotive, Food & Beverages, Office Supplies"
        
        final_prompt = final_prompt.replace("{__categories__}", categories_text)
        return final_prompt

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
                prompt_template = self._get_product_description_prompt(prompt)
                full_prompt = self._build_final_prompt(prompt_template, text, categories)
                
                payload = {
                    "text": text,
                    "prompt": full_prompt
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

    async def generate_promotional_audio_script(self, text: str, prompt: Optional[str] = None) -> str:
        """Generate a promotional audio script using the Mistral model microservice."""
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

                # Call the generate-text endpoint with promotional audio script prompt
                prompt_template = self._get_promotional_audio_script_prompt(prompt)
                full_prompt = self._build_final_prompt(prompt_template, text)
                payload = {
                    "text": text,
                    "prompt": full_prompt
                }
                
                async with session.post(f"{self.service_url}/generate-text", json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Mistral service error: {resp.status}, {error_text}")
                        return f"Service error: {resp.status}"
                    
                    result = await resp.json()
                    script = result.get("text", "")
                    logger.info("Mistral service generated promotional audio script successfully")
                    return script

        except aiohttp.ClientError as e:
            logger.error(f"Mistral service connection error: {str(e)}")
            return f"Service connection error: {str(e)}"
        except Exception as e:
            logger.error(f"Mistral promotional audio script generation error: {str(e)}")
            raise
