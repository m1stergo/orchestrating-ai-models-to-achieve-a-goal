"""
OpenAI adapter for text generation and image description.
"""
import logging
import asyncio
import re
import json
from openai import OpenAI
from typing import Optional, List

from app.config import settings
from .base import TextGenerationAdapter
from ..shared.prompts import get_product_description_prompt, get_promotional_audio_script_prompt

logger = logging.getLogger(__name__)


class OpenAIAdapter(TextGenerationAdapter):
    """OpenAI adapter for text generation."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = settings.OPENAI_TEXT_MODEL  # e.g., "gpt-4o-mini"
        self.model = None

        if self.is_available():
            self.model = OpenAI(api_key=self.api_key)

    def is_available(self) -> bool:
        """Check if the OpenAI API key is available."""
        available = bool(self.api_key and self.api_key.strip())
        if not available:
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        return available

    async def generate_text(self, text: str, prompt: Optional[str] = None, categories: Optional[List[str]] = None) -> str:
        """Generate text using OpenAI's text model."""
        if not self.is_available():
            raise ValueError("OpenAI API key is not configured.")

        final_prompt = get_product_description_prompt(prompt, text, categories)

        logger.info(f"Final prompt: {final_prompt}")
        try:
            result_text = await asyncio.to_thread(self.generate_text_sync, final_prompt)
            logger.info("OpenAI model generated text successfully")
            return result_text
        except Exception as e:
            logger.error(f"OpenAI text generation error: {e}")
            raise


    async def generate_promotional_audio_script(self, text: str, prompt: Optional[str] = None) -> str:
        """Generate a promotional audio script using OpenAI's text model."""
        if not self.is_available():
            raise ValueError("OpenAI API key is not configured.")

        final_prompt = get_promotional_audio_script_prompt(prompt, text)

        logger.info(f"Final promotional audio script prompt: {final_prompt}")
        try:
            result_text = await asyncio.to_thread(self.generate_text_sync, final_prompt)
            logger.info("OpenAI model generated promotional audio script successfully")
            return result_text
        except Exception as e:
            logger.error(f"OpenAI promotional audio script generation error: {e}")
            raise

    def generate_text_sync(self, full_prompt: str) -> str:
        """Synchronous method to generate text using OpenAI."""
        if self.model is None:
            self.model = OpenAI(api_key=self.api_key)

        result = self.model.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=1000,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        text = result.choices[0].message.content or ""
        return self._extract_json_from_response(text)
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON from response text that may contain markdown code blocks."""
        if not response_text:
            return response_text
            
        # Try to find JSON within markdown code blocks
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
            try:
                # Validate it's proper JSON by parsing and re-serializing
                parsed = json.loads(json_str)
                return json.dumps(parsed, ensure_ascii=False)
            except json.JSONDecodeError:
                logger.warning("Found JSON block but couldn't parse it, returning original")
                return response_text
        
        # If no code blocks, try to find JSON directly
        try:
            # Look for JSON object pattern
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                return json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError:
            pass
            
        # Return original if no valid JSON found
        return response_text

    async def warmup(self) -> str:
        """
        Warmup the OpenAI adapter.
        
        Returns:
            str with warmup status and information
        """
        if not self.is_available():
            raise ValueError("OpenAI API key is not configured.")
            
        logger.info("OpenAI warmup successful")
        return "OpenAI adapter is ready"