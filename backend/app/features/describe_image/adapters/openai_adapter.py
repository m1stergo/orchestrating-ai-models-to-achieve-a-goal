"""
OpenAI adapter for image description.
"""
import logging
from typing import Optional
from openai import OpenAI
from app.config import settings
from .base import ImageDescriptionAdapter

logger = logging.getLogger(__name__)


class OpenAIAdapter(ImageDescriptionAdapter):
    def __init__(self):
        super().__init__(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_VISION_MODEL,  # e.g., "gpt-4o"
            service_name="OpenAI"
        )
        self.model = OpenAI(api_key=self.api_key)
    
    async def inference(self, image_url: str, prompt: Optional[str] = None) -> str:
        logger.info(f"OpenAI: describing image from {image_url}")

        try:
            final_prompt, image_data = await self.get_inputs(image_url, prompt)
            
            result_text = await self.run_inference(
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
            
            logger.info("OpenAI model described image successfully")
            return result_text
        except Exception as e:
            logger.error(f"OpenAI image description error: {e}")
            raise
