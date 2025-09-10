"""
Chatterbox TTS adapter for text-to-speech generation.
"""
import logging
import aiohttp
import uuid
import aiofiles
from typing import Optional
from pathlib import Path
from app.config import settings

from .base import TextToSpeechAdapter

logger = logging.getLogger(__name__)


class ChatterboxAdapter(TextToSpeechAdapter):
    """Adapter for Chatterbox TTS service."""
    
    def __init__(self):
        self.service_url = settings.TTS_CHATTERBOX_URL
        self.timeout = aiohttp.ClientTimeout(total=60.0)  # TTS can take longer than regular API calls
    
    def is_available(self) -> bool:
        """Check if the Chatterbox service URL is available."""
        available = bool(self.service_url and self.service_url.strip())
        if not available:
            logger.warning("Chatterbox service URL not found. Set TTS_CHATTERBOX_URL environment variable.")
        return available
    
    async def generate_speech(self, text: str, audio_prompt_url: Optional[str] = None) -> bytes:
        """
        Generate speech using Chatterbox TTS service.
        
        Args:
            text: Text to convert to speech
            audio_prompt_url: Optional URL to audio prompt file for voice cloning
            
        Returns:
            bytes: Audio data as WAV bytes
        """
        if not self._is_available():
            raise ValueError("Chatterbox TTS service URL is not configured.")

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # First check if the service is healthy
                try:
                    health_url = f"{self.service_url}/healthz"
                    async with session.get(health_url) as health_resp:
                        health_data = await health_resp.json()
                        if not health_resp.ok or not health_data.get("loaded", False):
                            logger.error(f"Chatterbox TTS service not ready: {health_resp.status}")
                            raise Exception("Service not available. The model is still loading or not responding.")
                except Exception as e:
                    logger.error(f"Failed to check Chatterbox TTS service health: {str(e)}")
                    raise Exception("Service health check failed. The service may be down.")

                # Prepare request payload
                payload = {
                    "text": text
                }
                
                if audio_prompt_url:
                    payload["audio_prompt_url"] = audio_prompt_url
                
                # Call the generate-audio endpoint
                async with session.post(f"{self.service_url}/generate-audio", json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Chatterbox TTS service error: {resp.status}, {error_text}")
                        raise Exception(f"Service error: {resp.status}")
                    
                    # Return the audio bytes directly
                    audio_bytes = await resp.read()
                    logger.info("Chatterbox TTS service generated audio successfully")
                    return audio_bytes

        except aiohttp.ClientError as e:
            logger.error(f"Chatterbox TTS service connection error: {str(e)}")
            raise Exception(f"Service connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Chatterbox TTS adapter error: {str(e)}")
            raise
