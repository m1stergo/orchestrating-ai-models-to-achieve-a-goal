import os
import logging
from typing import Dict, Any
import httpx
from .base import BaseGenerateDescriptionStrategy

logger = logging.getLogger(__name__)


class GeminiStrategy(BaseGenerateDescriptionStrategy):
    """Google Gemini strategy for text generation."""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        # self.model = "gemini-1.5-flash"
        self.model = "gemini-2.5-pro"
        
    async def generate_description(self, text: str, prompt: str) -> str:
        """Generate description using Google Gemini."""
        if not self.api_key:
            raise ValueError("Gemini API key not found")
            
        # Combine the prompt with the input text
        full_prompt = f"{prompt}\n\nText to process:\n{text}"
        
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_prompt
                        }
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
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                if "candidates" not in result or not result["candidates"]:
                    raise Exception("No candidates in Gemini response")
                
                candidate = result["candidates"][0]
                if "content" not in candidate or "parts" not in candidate["content"]:
                    raise Exception("Invalid response structure from Gemini")
                
                generated_text = candidate["content"]["parts"][0]["text"].strip()
                
                logger.info(f"Gemini strategy generated description successfully")
                return generated_text
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Gemini API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error in Gemini strategy: {str(e)}")
            raise Exception(f"Gemini strategy failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Gemini API key is configured."""
        available = bool(self.api_key and self.api_key.strip())
        if not available:
            logger.warning("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        return available
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get Gemini strategy information."""
        return {
            "name": self.name,
            "model": self.model,
            "type": "api",
            "provider": "Google",
            "description": "Google Gemini text generation",
            "requires_api_key": True,
            "api_key_available": bool(self.api_key)
        }
