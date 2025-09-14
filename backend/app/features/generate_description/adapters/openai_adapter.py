"""
OpenAI adapter for text generation and image description.
"""
import logging
from openai import OpenAI
from typing import Optional

from app.config import settings
from app.features.generate_description.shared.utils import extract_json_from_response
from app.shared.api_adapter import ApiAdapter

logger = logging.getLogger(__name__)

class OpenAIAdapter(ApiAdapter):
    """OpenAI adapter for text generation."""

    def __init__(self):
        super().__init__(
            api_token=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_TEXT_MODEL,  # e.g., "gpt-4o-mini"
            service_name="OpenAI",
            model=OpenAI(api_key=settings.OPENAI_API_KEY)
        )
    
    async def infer(self, prompt: Optional[str] = None) -> str:
        logger.info(f"===== OpenAI: generating description with {prompt} =====")

        response = await self.run(
            lambda: extract_json_from_response(
                self.model.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.3,
                    response_format={"type": "json_object"}
                ).choices[0].message.content or ""
            )
        )
        
        return response
    