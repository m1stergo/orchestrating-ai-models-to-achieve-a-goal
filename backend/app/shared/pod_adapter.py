"""
RunPod adapter utility base class for AI model interactions.
"""
import logging
import aiohttp
import asyncio
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)


class PodAdapter:
    """
    Base utility class for adapters that interact with RunPod-based services.
    Contains common functionality for service communication, status checking, and polling.
    """

    def __init__(self, service_url: str, api_token: Optional[str] = None, 
                 service_name: str = "RunPod", timeout: int = 60, 
                 poll_interval: int = 5, max_retries: int = 40):
        """
        Initialize the RunPod adapter.
        
        Args:
            service_url: URL of the RunPod service
            api_token: Optional API token for authentication
            service_name: Name of the service for logging purposes
            timeout: Timeout in seconds for API calls
            poll_interval: Interval in seconds between polling attempts
            max_retries: Maximum number of polling retries
        """
        self.service_url = service_url
        self.api_token = api_token
        self.service_name = service_name
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.poll_interval = poll_interval
        self.max_retries = max_retries

    def _is_available(self) -> bool:
        """Check if the service URL is available."""
        available = bool(self.service_url and self.service_url.strip())
        if not available:
            logger.warning(f"{self.service_name} service URL not found.")
        return available

    async def _call_endpoint(self, endpoint: str, method: str = "POST", 
                           payload: Optional[Dict[str, Any]] = None, 
                           check_status: bool = True) -> Dict[str, Any]:
        """
        Call a RunPod service endpoint.
        
        Args:
            endpoint: API endpoint path (without the base URL)
            method: HTTP method to use (GET, POST, etc.)
            payload: JSON payload to send
            check_status: Whether to check and raise on non-200 status
            
        Returns:
            API response as a dictionary
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        } if self.api_token else {}

        url = f"{self.service_url}/{endpoint.lstrip('/')}"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with getattr(session, method.lower())(url, json=payload, headers=headers) as resp:
                    if check_status and resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"{self.service_name} service error: {resp.status}, {error_text}")
                        raise Exception(f"HTTP error: {resp.status}")
                    
                    return await resp.json()
        except aiohttp.ClientError as e:
            logger.error(f"{self.service_name} connection error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"{self.service_name} endpoint call error: {str(e)}")
            raise

    async def run_inference(self, payload: Dict[str, Any], action: str = "inference") -> Dict[str, Any]:
        """
        Run an inference job with the RunPod service.
        
        Args:
            payload: Dictionary containing input data for the model
            action: The action to perform (default: "inference")
            
        Returns:
            Dictionary with job result
        """
        if not self._is_available():
            raise ValueError(f"{self.service_name} service URL is not configured")
        
        # Format the payload for RunPod
        runpod_payload = {
            "input": {
                "action": action,
                **payload
            }
        }
        
        # Submit the job
        initial_result = await self._call_endpoint("run", "POST", runpod_payload)
        
        if initial_result.get("status") == "ERROR":
            raise Exception(initial_result.get("message") or "Unknown error")
            
        job_id = initial_result.get("id", "")
        logger.info(f"Waiting for {self.service_name} job {job_id} to complete...")
        logger.info(f"Initial response: {initial_result}")
        
        # Poll until job is complete
        final_result = await self._poll_until_complete(job_id)
        logger.info(f"Final result after polling: {final_result}")
        return final_result

    async def warmup(self) -> str:
        """
        Warmup the service by calling its warmup endpoint.
            
        Returns:
            str: String message with warmup status information
        """
        if not self._is_available():
            raise ValueError(f"{self.service_name} service URL is not configured")
        
        try:
            # Call the RunPod-compatible warmup endpoint
            payload = {
                "input": {
                    "action": "warmup"
                }
            }
            
            initial_result = await self._call_endpoint("run", "POST", payload)
            
            if initial_result.get("status") == "ERROR":
                raise Exception(initial_result.get("message"))
                
            job_id = initial_result.get("id", "")
            logger.info(f"Initial result WARMUP: {initial_result}")
            logger.info(f"Waiting for warmup job {job_id} to complete...")
            
            try:
                result = await self._poll_until_complete(job_id)
                # Siempre retornar un string con el mensaje de resultado
                return str(result.get("detail", {}).get("message", "Model warmed up successfully"))
            except Exception as e:
                logger.info(f"Job ID {job_id} not found, model likely already warmed up")
                return str(e)
                
        except Exception as e:
            logger.error(f"{self.service_name} warmup error: {str(e)}")
            raise
            
    async def _status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of a specific job.
        
        Args:
            job_id: Job ID to check status for
            
        Returns:
            Dictionary with job status information
        """
        try:
            timeout = aiohttp.ClientTimeout(total=5)  # Short timeout for status check
            async with aiohttp.ClientSession(timeout=timeout) as session:
                status_url = f"{self.service_url}/status/{job_id}"
                
                logger.info(f"Checking status for job {job_id} at URL: {status_url}")
                
                headers = {
                    "Authorization": f"Bearer {self.api_token}"
                } if self.api_token else {}
                
                async with session.get(status_url, headers=headers) as resp:
                    if resp.status == 404:
                        error_message = f"Job ID {job_id} not found"
                        logger.warning(error_message)
                        raise Exception(error_message)
                    elif resp.status != 200:
                        error_message = f"HTTP error: {resp.status} when checking status for job {job_id}"
                        logger.error(error_message)
                        return {
                            "status": "ERROR", 
                            "id": None, 
                            "detail": {
                                "status": "ERROR", 
                                "message": error_message, 
                                "data": ""
                            }
                        }
                    
                    result = await resp.json()
                    logger.info(f"Status response for job {job_id}: {result}")
                    
                    # Check if the result indicates the job doesn't exist
                    if result.get("status") == "ERROR" and "not found" in result.get("detail", {}).get("message", "").lower():
                        error_message = result.get("detail", {}).get("message", f"Job ID {job_id} not found")
                        logger.warning(error_message)
                        raise Exception(error_message)
                        
                    return result
                        
        except aiohttp.ClientError as e:
            logger.error(f"{self.service_name} status check connection error: {str(e)}")
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
            logger.error(f"{self.service_name} status check error: {str(e)}")
            return {
                "status": "ERROR", 
                "id": None, 
                "detail": {
                    "status": "ERROR", 
                    "message": f"Unexpected error: {str(e)}", 
                    "data": ""
                }
            }

    async def _poll_until_complete(self, job_id: str, interval: int = None, max_retries: int = None) -> Dict[str, Any]:
        """
        Poll a job until it's complete or until max retries is reached.
        
        Args:
            job_id: The job ID to poll
            interval: Seconds between polling attempts (defaults to self.poll_interval)
            max_retries: Maximum number of polling attempts (defaults to self.max_retries)
            
        Returns:
            Dictionary with job status
        """
        interval = interval or self.poll_interval
        max_retries = max_retries or self.max_retries
        retries = 0
        
        while retries < max_retries:
            # Check job status
            status_response = await self._status(job_id)

            # If job failed
            if status_response.get("status") == "ERROR":
                error_message = status_response.get("detail", {}).get("message", "")
                logger.error(f"Job {job_id} failed: {error_message}")
                return status_response

            job_status = status_response.get("status")
            detail_status = status_response.get("detail", {}).get("status")
            data = status_response.get("detail", {}).get("data", "")
            
            logger.info(f"Poll {retries}: job_status={job_status}, detail_status={detail_status} for job_id={job_id}")
            
            # Si tenemos datos o el estado es COMPLETED con IDLE, consideramos que el job está completo
            if data or (job_status == "COMPLETED" and detail_status == "IDLE"):
                logger.info(f"Job {job_id} completed successfully with data or IDLE status")
                return status_response
                
            # Si el status es COMPLETED pero no tiene datos ni es IDLE, también lo consideramos completo
            # Esto maneja el caso de servicios que retornan COMPLETED pero sin estado detail.status
            if job_status == "COMPLETED":
                logger.info(f"Job {job_id} completed with COMPLETED status but no IDLE flag")
                return status_response
                    
            # Wait before checking again
            retries += 1
            logger.info(f"Job {job_id} still in progress, retry {retries}/{max_retries}")
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
