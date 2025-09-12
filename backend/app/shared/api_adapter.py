"""
Base API adapter for direct integration with external APIs (OpenAI, Gemini, etc.).
Handles common patterns for API-based adapters.
"""
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar


logger = logging.getLogger(__name__)

T = TypeVar('T')

class   ApiAdapter(ABC):
    """
    Base class for API-based adapters that interact directly with external API services.
    Handles common functionality like availability checks, async-to-sync conversion, and error handling.
    """
    def __init__(self, api_key: str, model_name: str, service_name: str):
        """
        Initialize API adapter with common properties.
        
        Args:
            api_key: API key for the service
            model_name: Name of the model to use
            service_name: Human-readable name of the service for logging
        """
        self.api_key = api_key
        self.model_name = model_name
        self.service_name = service_name
        self.model = None

    def _is_available(self) -> bool:
        """Check if the API key is available."""
        available = bool(self.api_key and self.api_key.strip())
        if not available:
            logger.warning(f"{self.service_name} API key not found.")
        return available

    async def run_inference(self, 
                              sync_func: Callable[..., T], 
                              *args: Any, 
                              **kwargs: Any) -> T:
        """
        Run a synchronous function in an async context, initializing the model if needed.
        
        Args:
            sync_func: Synchronous function to run
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result from the synchronous function
        """
        if not self._is_available():
            raise ValueError(f"{self.service_name} API key is not configured.")
            
        try:
            # Run the synchronous function in a thread pool
            result = await asyncio.to_thread(sync_func, *args, **kwargs)
            logger.info(f"{self.service_name} executed task successfully")
            return result
        except Exception as e:
            logger.error(f"{self.service_name} execution error: {str(e)}")
            raise
    
    async def warmup(self) -> str:
        """
        Warmup the adapter.
        
        Returns:
            str with warmup status and information
        """
        if not self._is_available():
            raise ValueError(f"{self.service_name} API key is not configured.")
            
        logger.info(f"{self.service_name} warmup successful")
        return f"{self.service_name} adapter is ready"
