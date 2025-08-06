import logging
import asyncio
from openai import OpenAI
from .base import BaseGenerateDescriptionModel
from config import settings

logger = logging.getLogger(__name__)

class OpenAIModel(BaseGenerateDescriptionModel):
    """OpenAI GPT model for text generation using the official SDK."""

    def __init__(self):
        super().__init__()
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL  # ej: "gpt-4o-mini" o el que uses
        self._client = None

        if self.is_available():
            self._client = OpenAI(api_key=self.api_key)

    def is_available(self) -> bool:
        available = bool(self.api_key and self.api_key.strip())
        if not available:
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        return available

    async def generate_description(self, text: str, prompt: str) -> str:
        """Generate description using OpenAI SDK."""
        if not self.is_available():
            raise ValueError("OpenAI API key is not configured.")

        # Igual que tu versión previa
        full_prompt = f"{prompt}\n\nText to process:\n{text}"

        try:
            result_text = await asyncio.to_thread(self._generate_sync, full_prompt)
            logger.info("OpenAI model generated description successfully")
            return result_text
        except Exception as e:
            logger.error(f"OpenAI model error: {e}")
            raise

    def _generate_sync(self, full_prompt: str) -> str:
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)

        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=1000,
            temperature=0.7,
        )
        text = resp.choices[0].message.content or ""
        return text.strip()
