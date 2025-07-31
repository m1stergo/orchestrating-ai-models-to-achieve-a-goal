import os
import logging
from typing import Dict, Any
import httpx
from .base import BaseGenerateDescriptionStrategy

logger = logging.getLogger(__name__)


class OpenAIStrategy(BaseGenerateDescriptionStrategy):
    """OpenAI GPT-4 strategy for text generation."""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4o"
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    async def generate_description(self, text: str, prompt: str) -> str:
        """Generate description using OpenAI GPT-4."""
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Combine the prompt with the input text
        full_prompt = f"{prompt}\n\nText to process:\n{text}"
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                generated_text = result["choices"][0]["message"]["content"].strip()
                
                logger.info(f"OpenAI strategy generated description successfully")
                return generated_text
                
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"OpenAI API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error in OpenAI strategy: {str(e)}")
            raise Exception(f"OpenAI strategy failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if OpenAI API key is configured."""
        available = bool(self.api_key and self.api_key.strip())
        if not available:
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        return available
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get OpenAI strategy information."""
        return {
            "name": self.name,
            "model": self.model,
            "type": "api",
            "provider": "OpenAI",
            "description": "OpenAI GPT-4 text generation",
            "requires_api_key": True,
            "api_key_available": bool(self.api_key)
        }
