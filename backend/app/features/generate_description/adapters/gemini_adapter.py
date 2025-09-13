"""
Gemini adapter for text generation.
"""
import logging
import google.generativeai as genai
from typing import Optional

from app.config import settings
from .base import GenerateDescriptionAdapter
from ..shared.utils import extract_json_from_response

logger = logging.getLogger(__name__)


class GeminiAdapter(GenerateDescriptionAdapter):
    def __init__(self):
        super().__init__(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_TEXT_MODEL,  # e.g., "gemini-1.5-pro-latest"
            service_name="Gemini"
        )
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    async def inference(self, prompt: Optional[str] = None) -> str:
        """Run inference to generate text using Gemini's text model."""
        try:
            result_text = await self.run_inference(
                lambda: extract_json_from_response(
                    self.model.generate_content(
                        prompt,
                        generation_config={
                            "temperature": 0.7,
                            "max_output_tokens": 1000,
                        },
                    ).text
                )
            )
            logger.info("Gemini inference successfully")
            return result_text
        except Exception as e:
            logger.error(f"Gemini inference error: {e}")
            raise