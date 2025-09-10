"""
Qwen adapter for image description
"""
import logging
from typing import Optional

from app.config import settings
from .base import ImageDescriptionAdapter
from app.shared.api_adapter import ApiAdapter
from app.shared.pod_adapter import PodAdapter
from ..shared.utils import get_image_description_prompt

logger = logging.getLogger(__name__)


class QwenAdapter(PodAdapter, ImageDescriptionAdapter):
    def __init__(self):
        # Inicializar PodAdapter primero
        PodAdapter.__init__(self,
            service_url=settings.DESCRIBE_IMAGE_QWEN_URL,
            api_token=settings.EXTERNAL_API_TOKEN,
            service_name="Qwen",
            timeout=60,
            poll_interval=5,
            max_retries=40
        )
        
        # Luego inicializar ApiAdapter a través de ImageDescriptionAdapter
        ApiAdapter.__init__(self, 
            api_key="",  # No necesitamos una API key para servicios externos
            model_name="",  # No necesitamos un nombre de modelo para servicios externos
            service_name="Qwen"  # Sobreescribe el valor de PodAdapter, pero es el mismo
        )
        
        logger.info(f"QwenAdapter inicializado con service_url={self.service_url}")

    def _init_model(self) -> None:
        """No se necesita inicializar un modelo local para servicios externos."""
        # No es necesario código aquí para PodAdapter ya que usa un servicio externo
        pass
        
    # El método _is_available ya está implementado en PodAdapter
        
    async def inference(self, image_url: str, prompt: Optional[str] = None) -> str:
        """
        Run inference with Qwen to describe an image.
        
        Args:
            image_url: URL of the image to describe
            prompt: Optional custom prompt to use
            
        Returns:
            str: Description result
        """
        if not self._is_available():
            raise ValueError("Qwen service URL is not configured")

        try:
            final_prompt = get_image_description_prompt(prompt)
            
            payload = {
                "image_url": image_url,
                "prompt": final_prompt
            }
            
            final_result = await self.run_inference(payload)

            return final_result.get("detail", {}).get("data", "")

        except Exception as e:
            logger.error(f"Qwen adapter error: {str(e)}")
            raise
