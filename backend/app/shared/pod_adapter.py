"""
RunPod adapter utility base class for AI model interactions.
"""
import logging
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from .adapter import Adapter

from app.shared.schemas import PodResponse, ServiceResponse

logger = logging.getLogger(__name__)


class PodAdapter(Adapter):
    """
    Base utility class for adapters that interact with RunPod-based services.
    Contains common functionality for service communication, status checking, and polling.
    """

    def __init__(self, service_url: str, api_token: Optional[str] = None, 
                 service_name: str = "RunPod", model: Any = None, timeout: int = 60, 
                 poll_interval: int = 5, max_retries: int = 40):
        super().__init__(service_name, service_name, model, api_token)
        self.service_url = service_url
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
                           checkstatus: bool = True) -> PodResponse:
        """
        Call a RunPod service endpoint.
        
        Args:
            endpoint: API endpoint path (without the base URL)
            method: HTTP method to use (GET, POST, etc.)
            payload: JSON payload to send
            checkstatus: Whether to check and raise on non-200 status
            
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
                    if checkstatus and resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"{self.service_name} service error: {resp.status}, {error_text}")
                        raise Exception(f"HTTP error: {resp.status}")
                    
                    response_json = await resp.json()

                    if "output" in response_json and isinstance(response_json["output"], dict):
                        output_dict = response_json["output"]
                        service_response = ServiceResponse(
                            status=output_dict.get("status", ""),
                            message=output_dict.get("message", ""),
                            data=output_dict.get("data", "")
                        )
                        
                        return PodResponse(
                            status=response_json.get("status", "COMPLETED"),
                            id=response_json.get("id", ""),
                            output=service_response
                        )
                    else:
                        return PodResponse(
                            status=response_json.get("status", "COMPLETED"),
                            id=response_json.get("id", ""),
                            output=ServiceResponse(status="COMPLETED", message="", data="")
                        )
        except aiohttp.ClientError as e:
            logger.error(f"{self.service_name} connection error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"{self.service_name} endpoint call error: {str(e)}")
            raise

    async def run(self, payload: Dict[str, Any], action: str = "inference") -> ServiceResponse:
        try:
            if not self._is_available():
                raise ValueError(f"{self.service_name} service URL is not configured")
            
            runpod_payload = {
                "input": {
                    "action": action,
                    **payload
                }
            }
            
            initial_result = await self._call_endpoint("run", "POST", runpod_payload)

            if initial_result.status == "FAILED":
                return initial_result.output
                
            job_id = initial_result.id
            logger.info(f"===== Waiting for {self.service_name} job {job_id} to complete... =====")
            logger.info(f"===== Initial response: {initial_result} =====")
            
            final_result = await self._poll_until_complete(job_id)
            logger.info(f"===== Final result after polling: {final_result} =====")
            
            return final_result.output
            
        except Exception as e:
            logger.error(f"{self.service_name} run error: {str(e)}")
            return ServiceResponse(
                status="FAILED",
                message=f"{self.service_name} run error: {str(e)}",
                data=""
            )

    async def warmup(self) -> ServiceResponse:      
        try:
            if not self._is_available():
                raise ValueError(f"{self.service_name} service URL is not configured")
            
            # Call the RunPod-compatible warmup endpoint
            payload = {
                "input": {
                    "action": "warmup"
                }
            }
            
            initial_result = await self._call_endpoint("run", "POST", payload)

            if initial_result.status == "FAILED":
                return initial_result.output
                
            job_id = initial_result.id
            logger.info(f"===== Initial result WARMUP: {initial_result} =====")
            logger.info(f"===== Waiting for warmup job {job_id} to complete... =====")
            
            final_result = await self._poll_until_complete(job_id)

            return final_result.output
                
        except Exception as e:
            logger.error(f"{self.service_name} warmup error: {str(e)}")
            return ServiceResponse(
                status="FAILED",
                message=f"{self.service_name} warmup error: {str(e)}",
                data=""
            )
            
    async def pod_status(self, job_id: str) -> PodResponse:
        try:
            timeout = aiohttp.ClientTimeout(total=5)  # Short timeout for status check
            async with aiohttp.ClientSession(timeout=timeout) as session:
                status_url = f"{self.service_url}/status/{job_id}"
                
                logger.info(f"===== Checking status for job {job_id} at URL: {status_url} =====")
                
                headers = {
                    "Authorization": f"Bearer {self.api_token}"
                } if self.api_token else {}
                
                async with session.get(status_url, headers=headers) as resp:
                    result = await resp.json()
                    logger.info(f"===== Status response for job {job_id}: {result} =====")
                    
                    # Convertir el diccionario JSON a objetos Pydantic
                    if "output" in result and isinstance(result["output"], dict):
                        output_dict = result["output"]
                        service_response = ServiceResponse(
                            status=output_dict.get("status", "COMPLETED"),
                            message=output_dict.get("message", ""),
                            data=output_dict.get("data", "")
                        )
                        
                        # Check if the result indicates the job doesn't exist
                        if result.get("status") == "FAILED":
                            raise Exception(service_response.message or "Unknown error")
                            
                        return PodResponse(
                            status=result.get("status", ""),
                            id=result.get("id", ""),
                            output=service_response
                        )
                    else:
                        empty_service_response = ServiceResponse(status="COMPLETED", message="", data="")
                        
                        if result.get("status") == "FAILED":
                            raise Exception("Unknown error")
                            
                        return PodResponse(
                            status=result.get("status", ""),
                            id=result.get("id", ""),
                            output=empty_service_response
                        )
                        
        except aiohttp.ClientError as e:
            logger.error(f"===== {self.service_name} status check connection error: {str(e)} =====")
            return PodResponse(
                status="FAILED", 
                id="", 
                output=ServiceResponse(
                    status="FAILED", 
                    message=f"Connection error: {str(e)}", 
                    data=""
                )
            )
        except Exception as e:
            logger.error(f"===== {self.service_name} status check error: {str(e)} =====")
            return PodResponse(
                status="FAILED", 
                id="", 
                output=ServiceResponse(
                    status="FAILED", 
                    message=f"Unexpected error: {str(e)}", 
                    data=""
                )
            )

    async def _poll_until_complete(self, job_id: str, interval: int = None, max_retries: int = None) -> PodResponse:
        interval = interval or self.poll_interval
        max_retries = max_retries or self.max_retries
        retries = 0
        
        while retries < max_retries:
            # Check job status
            status_response = await self.pod_status(job_id)

            # If job failed
            if status_response.status == "FAILED":
                error_message = status_response.output.message if status_response.output else "Unknown error"
                logger.error(f"===== Job {job_id} failed: {error_message} =====")

                return status_response

            jobstatus = status_response.status
            outputstatus = status_response.output.status if status_response.output else ""
            
            logger.info(f"===== Poll {retries}: jobstatus={jobstatus}, outputstatus={outputstatus} for job_id={job_id} =====")
                
            if jobstatus == "COMPLETED":
                logger.info(f"===== Job {job_id} completed =====")
                return status_response
                    
            # Wait before checking again
            retries += 1
            logger.info(f"===== Job {job_id} still in progress, retry {retries}/{max_retries} =====")
            await asyncio.sleep(interval)
        
        # If we got here, we've exceeded max retries
        error_message = f"Timed out waiting for job {job_id} after {max_retries} retries"
        logger.error(f"===== {error_message} =====")
        return PodResponse(
            status="FAILED", 
            id="", 
            output=ServiceResponse(
                status="FAILED", 
                message=error_message, 
                data=""
            )
        )
