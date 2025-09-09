"""
Qwen adapter for image description
"""
import logging
import aiohttp
import asyncio
from typing import Optional

from app.config import settings
from .base import ImageDescriptionAdapter
from ..shared.prompts import get_image_description_prompt

logger = logging.getLogger(__name__)


class QwenAdapter(ImageDescriptionAdapter):
    def __init__(self):
        self.service_url = settings.DESCRIBE_IMAGE_QWEN_URL
        self.api_token = settings.QWEN_API_TOKEN
        self.timeout = aiohttp.ClientTimeout(total=60)  # 60 seconds timeout for inference
        self.poll_interval = 5  # Interval in seconds between polling attempts
        self.max_retries = 40   # Maximum number of polling retries

    def is_available(self) -> bool:
        """Check if the Qwen service URL is available."""
        available = bool(self.service_url and self.service_url.strip())
        if not available:
            logger.warning("Qwen service URL not found. Set DESCRIBE_IMAGE_QWEN_URL environment variable.")
        return available

    async def describe_image(self, image_url: str, prompt: Optional[str] = None) -> str:
        """Describe an image using the Qwen VL model microservice.
        
        Args:
            image_url: URL of the image to describe
            prompt: Optional custom prompt to use
            
        Returns:
            str: Description result
        """
        if not self.is_available():
            raise ValueError("Qwen service URL is not configured")

        # Use custom prompt or default
        final_prompt = get_image_description_prompt(prompt)

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Call the new RunPod-compatible endpoint
                payload = {
                    "input": {
                        "action": "inference",
                        "image_url": image_url,
                        "prompt": final_prompt
                    }
                }
                headers = {
                    "Authorization": f"Bearer {self.api_token}"
                } if self.api_token else {}
                async with session.post(f"{self.service_url}/run", json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP error: {resp.status}")
                    
                    # Parse initial response
                    initial_result = await resp.json()
                    

                    if initial_result.get("status") == "ERROR":
                        raise Exception(initial_result.get("message") or "Unknown error")
                        
                    job_id = initial_result.get("id", "")
                    
                    logger.info(f"Waiting for job {job_id} to complete...")
                    final_result = await self.poll_until_complete(job_id)

                    return final_result.get("detail", {}).get("data", "")

        except Exception as e:
            logger.error(f"Qwen adapter error: {str(e)}")
            raise

    async def warmup(self) -> str:
        """
        Warmup the Qwen service by calling its warmup endpoint.
            
        Returns:
            str with warmup status or job ID for polling
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Call the RunPod-compatible warmup endpoint
                payload = {
                    "input": {
                        "action": "warmup"
                    }
                }
                
                headers = {
                    "Authorization": f"Bearer {self.api_token}"
                } if self.api_token else {}
                async with session.post(f"{self.service_url}/run", json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP error: {resp.status}")
                    
                    initial_result = await resp.json()
                    
                    if initial_result.get("status") == "ERROR":
                        raise Exception(initial_result.get("message"))
                        
                    job_id = initial_result.get("id", "")

                    logger.info(f"Initial result WARMUP: {initial_result}")
                    
                    logger.info(f"Waiting for warmup job {job_id} to complete...")
                    try:
                        result = await self.poll_until_complete(job_id)
                        # poll_until_complete siempre devuelve un diccionario
                        return result.get("detail", {}).get("message", "Model warmed up successfully")
                    except Exception as e:
                        logger.info(f"Job ID {job_id} not found, model likely already warmed up")
                        
        except Exception as e:
            logger.error(f"Qwen warmup error: {str(e)}")
            raise
            
    # Internal use, has runpod signature        
    async def status(self, job_id: str) -> dict:
        """
        Check the status of the Qwen service or a specific job.
        
        Args:
            job_id: Job ID to check status for
            
        Returns:
            dict: Dictionary with job status information
        """
        if not self.is_available():
            return {
                "status": "ERROR", 
                "id": None, 
                "detail": {
                    "status": "ERROR", 
                    "message": "Qwen service URL is not configured", 
                    "data": ""
                }
            }

        try:
            timeout = aiohttp.ClientTimeout(total=5)  # Short timeout for status check
            async with aiohttp.ClientSession(timeout=timeout) as session:
                status_url = f"{self.service_url}/status/{job_id}"
                
                headers = {
                    "Authorization": f"Bearer {self.api_token}"
                } if self.api_token else {}
                
                async with session.get(status_url, headers=headers) as resp:
                    if resp.status == 404:
                        # Job ID no encontrado (404)
                        error_message = f"Job ID {job_id} not found"
                        logger.warning(error_message)
                        raise Exception(error_message)
                    elif resp.status != 200:
                        return {
                            "status": "ERROR", 
                            "id": None, 
                            "detail": {
                                "status": "ERROR", 
                                "message": f"HTTP error: {resp.status}", 
                                "data": ""
                            }
                        }
                    
                    # Get the complete response - ya es un diccionario, solo retornarlo
                    result = await resp.json()
                    
                    # Comprobar si el resultado indica que el job no existe
                    if result.get("status") == "ERROR" and "not found" in result.get("detail", {}).get("message", "").lower():
                        error_message = result.get("detail", {}).get("message", f"Job ID {job_id} not found")
                        logger.warning(error_message)
                        raise Exception(error_message)
                        
                    return result
                        
        except aiohttp.ClientError as e:
            logger.error(f"Qwen status check connection error: {str(e)}")
            return {
                "status": "ERROR", 
                "id": None, 
                "detail": {
                    "status": "ERROR", 
                    "message": f"Connection error: {str(e)}", 
                    "data": ""
                }
            }
        except Exception as e:
            logger.error(f"Qwen status check error: {str(e)}")
            return {
                "status": "ERROR", 
                "id": None, 
                "detail": {
                    "status": "ERROR", 
                    "message": f"Unexpected error: {str(e)}", 
                    "data": ""
                }
            }

    async def poll_until_complete(self, job_id: str, interval: int = None, max_retries: int = None) -> dict:
        """
        Poll a job until it's complete or until max retries is reached.
        
        Args:
            job_id: The job ID to poll
            interval: Seconds between polling attempts (defaults to self.poll_interval)
            max_retries: Maximum number of polling attempts (defaults to self.max_retries)
            
        Returns:
            dict: Dictionary with job status
        """
        interval = interval or self.poll_interval
        max_retries = max_retries or self.max_retries
        retries = 0
        
        while retries < max_retries:
            # Check job status
            status_response = await self.status(job_id)

            # If job failed
            if status_response.get("status") == "ERROR":
                error_message = status_response.get("detail", {}).get("message", "")
                logger.error(f"Job {job_id} failed: {error_message}")
                return status_response

            if status_response.get("status") == "COMPLETED" or status_response.get("status") == "IN_PROGRESS":
                if status_response.get("detail", {}).get("status") == "IDLE":
                    return status_response
                    
            # Wait before checking again
            retries += 1
            logger.debug(f"Job {job_id} still in progress, retry {retries}/{max_retries}")
            await asyncio.sleep(interval)
        
        # If we got here, we've exceeded max retries
        error_message = f"Timed out waiting for job {job_id} after {max_retries} retries"
        logger.error(error_message)
        return {
            "status": "ERROR", 
            "id": job_id, 
            "detail": {
                "status": "ERROR", 
                "message": error_message, 
                "data": ""
            }
        }