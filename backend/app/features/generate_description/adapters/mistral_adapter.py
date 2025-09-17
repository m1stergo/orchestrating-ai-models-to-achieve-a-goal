"""
Mistral adapter for text generation
"""
import logging
from typing import Optional, List
from app.config import settings
from app.shared.pod_adapter import PodAdapter
from app.features.generate_description.shared.utils import get_product_description_prompt, get_promotional_audio_script_prompt

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
        full_prompt = get_product_description_prompt(custom_prompt=prompt, categories=categories)
        text = "# MY PRODUCT:\n" + text

        logger.info(f"===== Mistral: generating description with {full_prompt} == {text} =====")
        
        payload = {
            "text": text,
            "prompt": full_prompt
        }
        
        response = await self.run(payload)

        return response

    async def infer_audio_script(self, text: str, prompt: Optional[str] = None) -> str:
        full_prompt = get_promotional_audio_script_prompt(custom_prompt=prompt)
        text = "# PRODUCT DESCRIPTION:\n" + text

        logger.info(f"===== Mistral: generating audio script with {full_prompt} == {text} =====")
        
        payload = {
            "text": text,
            "prompt": full_prompt
        }
        
        response = await self.run(payload)

        return response