"""
Mistral adapter for text generation
"""
import logging
from typing import Optional, List, Dict, Any
from app.config import settings
from app.shared.pod_adapter import PodAdapter
from app.shared.api_adapter import ApiAdapter
from .base import GenerateDescriptionAdapter
from ..shared.utils import get_product_description_prompt, get_promotional_audio_script_prompt

logger = logging.getLogger(__name__)


class MistralAdapter(PodAdapter, GenerateDescriptionAdapter):
    def __init__(self):
        # Mantener llamadas separadas para inicializar cada clase base correctamente
        PodAdapter.__init__(self,
            service_url=settings.GENERATE_DESCRIPTION_MISTRAL_URL,
            api_token=settings.EXTERNAL_API_TOKEN,
            service_name="Mistral",
            timeout=60,
            poll_interval=5,
            max_retries=40
        )
        
        ApiAdapter.__init__(self, 
            api_key="",  # No necesitamos una API key para servicios externos
            model_name="",  # No necesitamos un nombre de modelo para servicios externos
            service_name="Mistral"  # Esto sobreescribirá el valor de PodAdapter, pero es el mismo
        )
    
    def _init_model(self) -> None:
        """No se necesita inicializar un modelo local para servicios externos."""
        # No es necesario código aquí para PodAdapter ya que usa un servicio externo
        pass
    
    async def inference_text(self, text: str, prompt: Optional[str] = None, categories: Optional[List[str]] = None) -> str:
        """
        Run inference with Mistral to generate text.
        
        Args:
            text: Input text to process
            prompt: Optional custom prompt
            categories: Optional list of available product categories
            
        Returns:
            str: Generated text
        """
        if not self._is_available():
            raise ValueError("Mistral service URL is not configured.")

        try:
            # Prepare the prompt
            full_prompt = get_product_description_prompt(custom_prompt=prompt, product_description=text, categories=categories)
            
            # Prepare payload for the model
            payload = {
                "text": text,
                "prompt": full_prompt
            }
            
            # Run inference through the base class
            final_result = await self.run_inference(payload)

            # Extract generated text
            generated_text = final_result.get("detail", {}).get("data", "")
            
            logger.info("Mistral service generated text successfully")
            return generated_text

        except Exception as e:
            logger.error(f"Mistral adapter error: {str(e)}")
            raise

    async def generate_promotional_audio_script(self, text: str, prompt: Optional[str] = None) -> str:
        """Generate a promotional audio script using the Mistral model microservice with polling."""
        result = await self.inference_promotional_audio(text=text, prompt=prompt)
        return result
    
    async def inference_promotional_audio(self, text: str, prompt: Optional[str] = None) -> str:
        """
        Run inference with Mistral to generate a promotional audio script.
        
        Args:
            text: Input text to transform
            prompt: Optional custom prompt
            
        Returns:
            str: Generated promotional audio script
        """
        if not self._is_available():
            raise ValueError("Mistral service URL is not configured.")

        try:
            # Prepare the prompt
            full_prompt = get_promotional_audio_script_prompt(custom_prompt=prompt, text=text)
            
            # Prepare payload for the model
            payload = {
                "text": text,
                "prompt": full_prompt
            }
            
            # Run inference through the base class with specific action
            final_result = await self.run_inference(payload, action="generate_promotional_audio")

            # Extract generated text
            generated_script = final_result.get("detail", {}).get("data", "")
            
            if not generated_script:
                logger.warning(f"Empty result from promotional audio generation")
                
            logger.info("Mistral service generated promotional audio script successfully")
            return generated_script

        except Exception as e:
            logger.error(f"Mistral promotional audio script generation error: {str(e)}")
            raise

    async def warmup(self) -> str:
        """
        Warmup the Mistral service by calling its warmup endpoint.
            
        Returns:
            str with warmup status or job ID for polling
        """
        try:
            result = await super().warmup()
            return result if isinstance(result, str) else "Model warmed up successfully"
        except Exception as e:
            logger.error(f"Mistral warmup error: {str(e)}")
            raise
            
    # Override method to add specific logging
    async def status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of the Mistral service or a specific job.
        
        Args:
            job_id: Job ID to check status for
            
        Returns:
            dict: Dictionary with job status information
        """
        return await super().status(job_id)
