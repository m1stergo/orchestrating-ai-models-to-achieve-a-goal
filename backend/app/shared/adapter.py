"""
Base API adapter for direct integration with external APIs (OpenAI, Gemini, etc.).
Handles common patterns for API-based adapters.
"""
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar, Optional
from app.shared.schemas import ServiceResponse

logger = logging.getLogger(__name__)

T = TypeVar('T')

class Adapter(ABC):
    def __init__(self, model_name: str, service_name: str, model: Any, api_token: Optional[str] = None):
        self.model_name = model_name
        self.service_name = service_name
        self.model = model
        self.status = "COLD"
        self.api_token = api_token
        
    @abstractmethod
    def _is_available(self) -> bool:
        pass

    async def run(self, 
            sync_func: Callable[..., T], 
            *args: Any, 
            **kwargs: Any) -> ServiceResponse[T]:
        try:
            if not self._is_available():
                raise ValueError(f"{self.service_name} API key is not configured.")
            # Run the synchronous function in a thread pool
            result = await asyncio.to_thread(sync_func, *args, **kwargs)
            logger.info(f"==== {self.service_name} executed task successfully ====")
            
            return ServiceResponse(
                status="IDLE",
                message=f"{self.service_name} executed task successfully",
                data=result
            )
        except Exception as e:
            logger.error(f"==== {self.service_name} execution error: {str(e)} ====")
            return ServiceResponse(
                status="FAILED",
                message=f"{self.service_name} execution error: {str(e)}",
                data=""
            )
    
    async def warmup(self) -> ServiceResponse:
        try:
            if not self._is_available():
                raise ValueError(f"{self.service_name} API key is not configured.")
            
            logger.info(f"==== Warming up {self.service_name}... ====")
            logger.warning(f"==== Warming up {self.service_name}... ====")
            logger.error(f"==== Warming up {self.service_name}... ====")
            
            return ServiceResponse(
                status="IDLE",
                message=f"{self.service_name} warmup successful",
                data=""
            )
        except Exception as e:
            logger.error(f"==== {self.service_name} warmup error: {str(e)} ====")
            return ServiceResponse(
                status="FAILED",
                message=f"{self.service_name} warmup error: {str(e)}",
                data=""
            )
