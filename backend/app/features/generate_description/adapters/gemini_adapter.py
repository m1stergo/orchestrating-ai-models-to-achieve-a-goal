"""
Gemini adapter for text generation.
"""
import logging
import google.generativeai as genai
from typing import Optional

from app.config import settings
from app.shared.api_adapter import ApiAdapter
from app.features.generate_description.shared.utils import extract_json_from_response

logger = logging.getLogger(__name__)


class GeminiAdapter(ApiAdapter):
    def __init__(self):
        super().__init__(
            api_token=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_TEXT_MODEL,  # e.g., "gemini-1.5-pro-latest"
            service_name="Gemini",
        )
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    async def infer(self, prompt: Optional[str] = None) -> str:
        """Run inference to generate text using Gemini's text model."""
        response = await self.run(
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

        return response