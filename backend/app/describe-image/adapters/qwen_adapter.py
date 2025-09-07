"""
Qwen adapter for image description
"""
import logging
import aiohttp
from typing import Optional

from app.config import settings
from .base import ImageDescriptionAdapter
from ..schemas import StandardResponse
from ..shared.prompts import get_image_description_prompt

logger = logging.getLogger(__name__)


class QwenAdapter(ImageDescriptionAdapter):
    def __init__(self):
        self.service_url = settings.DESCRIBE_IMAGE_QWEN_URL
        self.api_token = settings.QWEN_API_TOKEN
        self.timeout = aiohttp.ClientTimeout(total=60)  # 60 seconds timeout for inference

    def is_available(self) -> bool:
        """Check if the Qwen service URL is available."""
        available = bool(self.service_url and self.service_url.strip())
        if not available:
            logger.warning("Qwen service URL not found. Set DESCRIBE_IMAGE_QWEN_URL environment variable.")
        return available

    async def describe_image(self, image_url: str, prompt: Optional[str] = None) -> StandardResponse:
        """Describe an image using the Qwen VL model microservice."""
        if not self.is_available():
            return self.format_error("Qwen service URL is not configured")

        # Use custom prompt or default
        final_prompt = get_image_description_prompt(prompt)

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Call the new RunPod-compatible endpoint
                payload = {
                    "input": {
                        "action": "inference",
                        "image_url": image_url,
                        "prompt": final_prompt
                    }
                }
                headers = {
                    "Authorization": f"Bearer {self.api_token}"
                } if self.api_token else {}
                async with session.post(f"{self.service_url}/run", json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        return self.format_error(f"HTTP error: {resp.status}")
                    
                    result = await resp.json()
                    details = result.get("details", {})

                    logger.info(f"#######\n#########\n######## Qwen describe image result: {result}")

                    return self.format_response(
                        status=result.get("status", "ERROR"),
                        id=result.get("id", ""),
                        detail_status=details.get("status", "IDLE"),
                        detail_message=details.get("message", ""),
                        detail_data=details.get("data", "")
                    )

        except aiohttp.ClientError as e:
            logger.error(f"Qwen service connection error: {str(e)}")
            return self.format_error(f"Connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Qwen adapter error: {str(e)}")
            return self.format_error(f"Unexpected error: {str(e)}")

    async def warmup(self) -> StandardResponse:
        """
        Warmup the Qwen service by calling its warmup endpoint.
        
        Returns:
            StandardResponse with warmup status
        """
        if not self.is_available():
            return self.format_error("Qwen service URL is not configured")

        try:
            timeout = aiohttp.ClientTimeout(total=10)  # Short timeout for warmup call
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Call the RunPod-compatible warmup endpoint
                payload = {
                    "input": {
                        "action": "warmup"
                    }
                }
                
                headers = {
                    "Authorization": f"Bearer {self.api_token}"
                } if self.api_token else {}
                async with session.post(f"{self.service_url}/run", json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        return self.format_error(f"HTTP error: {resp.status}")
                    
                    # Get the complete response
                    result = await resp.json()
                    details = result.get("details", {})
                    
                    return self.format_response(
                        status=result.get("status", "ERROR"),
                        id=result.get("id", ""),
                        detail_status=details.get("status", "IDLE"),
                        detail_message=details.get("message", ""),
                        detail_data=details.get("data", "")
                    )
                        
        except aiohttp.ClientError as e:
            logger.error(f"Qwen warmup connection error: {str(e)}")
            return self.format_error(f"Connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Qwen warmup error: {str(e)}")
            return self.format_error(f"Unexpected error: {str(e)}")

    async def status(self, job_id: str = "status-check") -> StandardResponse:
        """
        Check the status of the Qwen service.
        
        Args:
            job_id: Job ID to check status for (defaults to "status-check")
            
        Returns:
            StandardResponse with service status
        """
        if not self.is_available():
            return self.format_error("Qwen service URL is not configured")

        try:
            timeout = aiohttp.ClientTimeout(total=5)  # Short timeout for status check
            async with aiohttp.ClientSession(timeout=timeout) as session:
                status_url = f"{self.service_url}/status/{job_id}"
                
                headers = {
                    "Authorization": f"Bearer {self.api_token}"
                } if self.api_token else {}
                async with session.get(status_url, headers=headers) as resp:
                    if resp.status != 200:
                        return self.format_error(f"HTTP error: {resp.status}")
                    
                    # Get the complete response
                    result = await resp.json()
                    details = result.get("details", {})

                    return self.format_response(
                        status=result.get("status", "ERROR"),
                        id=result.get("id", ""),
                        detail_status=details.get("status", "IDLE"),
                        detail_message=details.get("message", ""),
                        detail_data=details.get("data", "")
                    )
                        
        except aiohttp.ClientError as e:
            logger.error(f"Qwen status check connection error: {str(e)}")
            return self.format_error(f"Connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Qwen status check error: {str(e)}")
            return self.format_error(f"Unexpected error: {str(e)}")
            
