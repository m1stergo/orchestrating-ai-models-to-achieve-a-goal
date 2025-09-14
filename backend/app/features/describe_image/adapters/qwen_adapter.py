"""
Qwen adapter for image description
"""
import logging
from typing import Optional

from app.config import settings
from app.shared.pod_adapter import PodAdapter
from app.shared.schemas import ServiceResponse
from ..shared.prompts import get_image_description_prompt

logger = logging.getLogger(__name__)

class QwenAdapter(PodAdapter):
    def __init__(self):
        super().__init__(
            service_url=settings.DESCRIBE_IMAGE_QWEN_URL,
            api_token=settings.EXTERNAL_API_TOKEN,
            service_name="Qwen",
            timeout=60,
            poll_interval=5,
            max_retries=40
        )
        
    async def infer(self, image_url: str, prompt: Optional[str] = None) -> ServiceResponse:
        final_prompt = get_image_description_prompt(prompt)
        
        payload = {
            "image_url": image_url,
            "prompt": final_prompt
        }
        
        response = await self.run(payload)
        
        return response
