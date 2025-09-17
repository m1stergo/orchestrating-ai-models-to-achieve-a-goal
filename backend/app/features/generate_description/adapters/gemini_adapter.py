"""
Gemini adapter for text generation.
"""
import logging
import google.generativeai as genai
from typing import Optional, List

from app.config import settings
from app.shared.api_adapter import ApiAdapter
from app.features.generate_description.shared.utils import extract_json_from_response, get_product_description_prompt, get_promotional_audio_script_prompt

logger = logging.getLogger(__name__)


class GeminiAdapter(ApiAdapter):
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        super().__init__(
            api_token=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_TEXT_MODEL,  # e.g., "gemini-1.5-pro-latest"
            service_name="Gemini",
            model=genai.GenerativeModel(settings.GEMINI_TEXT_MODEL)
        )

    async def infer(self, text: str, prompt: Optional[str] = None, categories: Optional[List[str]] = None) -> str:
        full_prompt = get_product_description_prompt(custom_prompt=prompt, categories=categories)
        full_prompt += "\n\n # MY PRODUCT:\n" + text

        logger.info(f"===== Gemini: generating description with {full_prompt} == {text} =====")

        
        """Run inference to generate text using Gemini's text model."""
        response = await self.run(
            lambda: extract_json_from_response(
                self.model.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 1000,
                    },
                ).text
            )
        )

        return response

    async def infer_audio_script(self, text: str, prompt: Optional[str] = None) -> str:
        full_prompt = get_promotional_audio_script_prompt(custom_prompt=prompt)
        full_prompt += "\n\n # PRODUCT DESCRIPTION:\n" + text

        logger.info(f"===== Gemini: generating audio script with {full_prompt} == {text} =====")

        
        """Run inference to generate text using Gemini's text model."""
        response = await self.run(
            lambda: extract_json_from_response(
                self.model.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 1000,
                    },
                ).text
            )
        )

        return response