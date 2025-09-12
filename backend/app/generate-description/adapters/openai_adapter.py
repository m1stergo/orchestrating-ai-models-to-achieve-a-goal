"""
OpenAI adapter for text generation and image description.
"""
import logging
from openai import OpenAI
from typing import Optional

from app.config import settings
from .base import GenerateDescriptionAdapter
from ..shared.utils import extract_json_from_response

logger = logging.getLogger(__name__)

class OpenAIAdapter(GenerateDescriptionAdapter):
    """OpenAI adapter for text generation."""

    def __init__(self):
        super().__init__(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_TEXT_MODEL,  # e.g., "gpt-4o-mini"
            service_name="OpenAI"
        )
        self.model = OpenAI(api_key=self.api_key)
    
    async def inference(self, prompt: Optional[str] = None) -> str:
        """Run inference to generate text using OpenAI's text model."""
        try:
            # Usar lambda para ejecutar la llamada directamente
            result_text = await self.run_inference(
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
            logger.info("OpenAI inference successfully")
            return result_text
        except Exception as e:
            logger.error(f"OpenAI inference error: {e}")
            raise
    