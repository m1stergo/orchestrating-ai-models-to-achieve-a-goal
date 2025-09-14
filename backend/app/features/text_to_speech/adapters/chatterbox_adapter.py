"""
Chatterbox TTS adapter for text_to_speech generation.
"""
import logging
from typing import Optional

from app.config import settings
from app.shared.pod_adapter import PodAdapter
from app.shared.schemas import ServiceResponse

logger = logging.getLogger(__name__)

class ChatterboxAdapter(PodAdapter):
    """Adapter for Chatterbox TTS service."""
    def __init__(self):
        # Inicializar PodAdapter primero
        super().__init__(
            service_url=settings.TTS_CHATTERBOX_URL,
            api_token=settings.EXTERNAL_API_TOKEN,
            service_name="Chatterbox",
            timeout=60,
            poll_interval=5,
            max_retries=40
        )

    async def infer(self, text: str, voice_url: Optional[str] = None) -> ServiceResponse:
        payload = {
            "text": text
        }
        
        if voice_url:
            payload["voice_url"] = voice_url

        response = await self.run_inference(payload)
        
        return response
