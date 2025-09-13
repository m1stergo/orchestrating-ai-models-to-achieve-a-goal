"""
Base adapter interfaces for AI models.
"""
from typing import Optional, List
from app.shared.api_adapter import ApiAdapter
from ..shared.utils import get_product_description_prompt, get_promotional_audio_script_prompt

class GenerateDescriptionAdapter(ApiAdapter):
    async def inference_text(self, text: str, prompt: Optional[str] = None, categories: Optional[List[str]] = None) -> str:
        final_prompt = get_product_description_prompt(custom_prompt=prompt, product_description=text, categories=categories)
        return await self.inference(final_prompt)

    async def inference_promotional_audio(self, text: str, prompt: Optional[str] = None) -> str:
        final_prompt = get_promotional_audio_script_prompt(custom_prompt=prompt, text=text)
        return await self.inference(final_prompt)
