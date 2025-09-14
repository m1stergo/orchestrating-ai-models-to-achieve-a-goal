"""
OpenAI adapter for image description.
"""
import logging
from typing import Optional
from openai import OpenAI
from app.config import settings
from app.shared.api_adapter import ApiAdapter
from app.shared.schemas import ServiceResponse
from ..shared.prompts import get_image_description_prompt
from ..shared.utils import convert_image_to_base64

logger = logging.getLogger(__name__)


class OpenAIAdapter(ApiAdapter):
    def __init__(self):
        super().__init__(
            api_token=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_VISION_MODEL,  # e.g., "gpt-4o"
            service_name="OpenAI",
            model=OpenAI(api_key=settings.OPENAI_API_KEY)
        )
    
    async def infer(self, image_url: str, prompt: Optional[str] = None) -> ServiceResponse:
        logger.info(f"===== OpenAI: describing image from {image_url} =====")

        final_prompt = get_image_description_prompt(prompt)
        image_data = await convert_image_to_base64(image_url)
            
        response = await self.run(
            lambda: self.model.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": final_prompt},
                        {"type": "image_url", "image_url": {"url": image_data}}
                    ]
                }],
                max_tokens=500,
                temperature=0.7,
            ).choices[0].message.content or ""
        )
        
        return response
