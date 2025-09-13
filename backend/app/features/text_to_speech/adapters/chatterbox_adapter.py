"""
Chatterbox TTS adapter for text_to_speech generation.
"""
import logging
import aiohttp
from typing import Optional

from app.config import settings
from .base import TextToSpeechAdapter
from app.shared.api_adapter import ApiAdapter
from app.shared.pod_adapter import PodAdapter

logger = logging.getLogger(__name__)

class ChatterboxAdapter(PodAdapter, TextToSpeechAdapter):
    """Adapter for Chatterbox TTS service."""
    def __init__(self):
        # Inicializar PodAdapter primero
        PodAdapter.__init__(self,
            service_url=settings.TTS_CHATTERBOX_URL,
            api_token=settings.EXTERNAL_API_TOKEN,
            service_name="Chatterbox",
            timeout=60,
            poll_interval=5,
            max_retries=40
        )

        # Luego inicializar ApiAdapter a través de ImageDescriptionAdapter
        ApiAdapter.__init__(self, 
            api_key="",  # No necesitamos una API key para servicios externos
            model_name="",  # No necesitamos un nombre de modelo para servicios externos
            service_name="Chatterbox"  # Sobreescribe el valor de PodAdapter, pero es el mismo
        )

        logger.info(f"ChatterboxAdapter inicializado con service_url={self.service_url}")
    
    async def inference(self, text: str, voice_url: Optional[str] = None) -> str:
        """
        Generate speech using Chatterbox TTS service.
        
        Args:
            text: Text to convert to speech
            voice_url: Optional URL to audio prompt file for voice cloning
            
        Returns:
            str: Audio URL
        """
        if not self._is_available():
            raise ValueError("Chatterbox TTS service URL is not configured.")

        try:
            payload = {
                "text": text
            }
            
            if voice_url:
                payload["voice_url"] = voice_url

            final_result = await self.run_inference(payload)
            
            logger.info("Chatterbox TTS service generated audio successfully")
            return final_result.get("detail", {}).get("data", "")

        except Exception as e:
            logger.error(f"Chatterbox TTS adapter error: {str(e)}")
            raise
