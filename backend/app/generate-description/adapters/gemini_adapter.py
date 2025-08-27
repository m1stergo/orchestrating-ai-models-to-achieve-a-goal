"""
Gemini adapter for text generation.
"""
import logging
import asyncio
import google.generativeai as genai
from typing import Optional, List

from app.config import settings
from .base import TextGenerationAdapter
from ..shared.prompts import get_product_description_prompt, get_promotional_audio_script_prompt, build_final_prompt

logger = logging.getLogger(__name__)


class GeminiAdapter(TextGenerationAdapter):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_TEXT_MODEL  # e.g., "gemini-1.5-pro-latest"
        self.model = None
        
        if self.is_available():
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)

    def is_available(self) -> bool:
        """Check if the Gemini API key is available."""
        ok = bool(self.api_key and self.api_key.strip())
        if not ok:
            logger.warning("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        return ok

    async def generate_text(self, text: str, prompt: Optional[str] = None, categories: Optional[List[str]] = None) -> str:
        """Generate text using Gemini's text model."""
        logger.info("Gemini generating text for input text")

        if not self.is_available():
            raise ValueError("Gemini API key is not configured.")

        prompt_template = get_product_description_prompt(prompt)
        full_prompt = build_final_prompt(prompt_template, text, categories)

        try:
            result_text = await asyncio.to_thread(self.generate_text_sync, full_prompt)
            logger.info("Gemini text generated successfully")
            return result_text.strip() if result_text else "No response generated"
        except Exception as e:
            logger.error(f"Gemini text generation error: {e}")
            raise

    async def generate_promotional_audio_script(self, text: str, prompt: Optional[str] = None) -> str:
        """Generate a promotional audio script using Gemini's text model."""
        logger.info("Gemini generating promotional audio script for input text")

        if not self.is_available():
            raise ValueError("Gemini API key is not configured.")

        prompt_template = get_promotional_audio_script_prompt(prompt)
        full_prompt = build_final_prompt(prompt_template, text)

        try:
            result_text = await asyncio.to_thread(self.generate_text_sync, full_prompt)
            logger.info("Gemini promotional audio script generated successfully")
            return result_text.strip() if result_text else "No response generated"
        except Exception as e:
            logger.error(f"Gemini promotional audio script generation error: {e}")
            raise

    def generate_text_sync(self, full_prompt: str) -> str:
        if self.model is None:
            # Fallback si el modelo no se inicializó en el constructor
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            
        result = self.model.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "max_output_tokens": 1000,
            },
        )

        return result.text
