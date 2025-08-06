import logging
import asyncio
import google.generativeai as genai

from typing import Optional
from .base import BaseGenerateDescriptionModel
from config import settings

logger = logging.getLogger(__name__)

class GeminiModel(BaseGenerateDescriptionModel):
    """Model for text generation using Google Gemini SDK."""

    def __init__(self):
        super().__init__()
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL  # ej: "gemini-1.5-pro-latest"
        self._model = None

        if self.is_available():
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)

    def is_available(self) -> bool:
        ok = bool(self.api_key and self.api_key.strip())
        if not ok:
            logger.warning("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        return ok

    async def generate_description(self, text: str, prompt: str) -> str:
        """Generate description using Google Gemini SDK."""
        logger.info("GeminiModel: generating description for input text")

        if not self.is_available():
            raise ValueError("Gemini API key is not configured. Set GEMINI_API_KEY environment variable.")

        # Armamos el prompt final igual que en tu versión HTTP
        full_prompt = f"{prompt}\n\nText to process:\n{text}"

        # Ejecutamos la llamada del SDK (sincrónica) en un thread para no bloquear
        try:
            result_text = await asyncio.to_thread(self._generate_sync, full_prompt)
            logger.info("GeminiModel: description generated successfully")
            return result_text.strip() if result_text else "No response generated"
        except Exception as e:
            logger.error(f"GeminiModel error: {e}")
            raise

    def _generate_sync(self, full_prompt: str) -> str:
        """Llamada síncrona al SDK. Se ejecuta en thread desde generate_description."""
        if self._model is None:
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)

        # Config de generación similar a tu payload original
        result = self._model.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "max_output_tokens": 1000,
            },
        )

        # El SDK ya expone .text con el mejor candidato
        return (result.text or "").strip()
