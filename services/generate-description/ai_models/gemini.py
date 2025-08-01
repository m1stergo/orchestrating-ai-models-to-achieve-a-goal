import httpx
import logging
from typing import Dict, Any
from .base import BaseGenerateDescriptionModel
from config import settings

logger = logging.getLogger(__name__)

class GeminiModel(BaseGenerateDescriptionModel):
    """Model for text generation using Google Gemini API."""

    def __init__(self):
        super().__init__()
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = settings.GEMINI_MODEL

    def is_available(self) -> bool:
        """Check if Gemini API key is configured."""
        available = bool(self.api_key and self.api_key.strip())
        if not available:
            logger.warning("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        return available

    async def generate_description(self, text: str, prompt: str) -> str:
        """Generate description using Google Gemini."""
        logger.info(f"GeminiModel: generating description for input text")

        if not self.is_available():
            raise ValueError("Gemini API key is not configured. Set GEMINI_API_KEY environment variable.")

        # Combine the prompt with the input text
        full_prompt = f"{prompt}\n\nText to process:\n{text}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1000,
            }
        }

        headers = {"Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{self.model}:generateContent",
                    headers=headers,
                    json=payload,
                    params={"key": self.api_key}
                )
                response.raise_for_status()
                result = response.json()
                
                # Extract the generated text
                description = self._parse_response(result)
                logger.info("GeminiModel: description generated successfully")
                return description
        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Gemini API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"GeminiModel error: {str(e)}")
            raise

    def _parse_response(self, result: Dict[str, Any]) -> str:
        """Parse response from Gemini API response."""
        try:
            candidates = result.get("candidates", [])
            if not candidates:
                return "No response generated"
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])

            if not parts:
                return "No response generated"
            
            output = parts[0].get("text", "No response generated")
            return output.strip()
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return f"Error processing response: {str(e)}"