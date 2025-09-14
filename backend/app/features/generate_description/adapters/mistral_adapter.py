"""
Mistral adapter for text generation
"""
import logging
from typing import Optional, List
from app.config import settings
from app.shared.pod_adapter import PodAdapter
from app.features.generate_description.shared.utils import get_product_description_prompt

logger = logging.getLogger(__name__)


class MistralAdapter(PodAdapter):
    def __init__(self):
        super().__init__(
            service_url=settings.GENERATE_DESCRIPTION_MISTRAL_URL,
            api_token=settings.EXTERNAL_API_TOKEN,
            service_name="Mistral",
            timeout=60,
            poll_interval=5,
            max_retries=40
        )
    
    async def infer(self, text: str, prompt: Optional[str] = None, categories: Optional[List[str]] = None) -> str:
        full_prompt = get_product_description_prompt(custom_prompt=prompt, product_description=text, categories=categories)
        
        payload = {
            "text": text,
            "prompt": full_prompt
        }
        
        response = await self.run(payload)

        return response