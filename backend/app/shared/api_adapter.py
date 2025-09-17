"""
Base API adapter for direct integration with external APIs (OpenAI, Gemini, etc.).
Handles common patterns for API-based adapters.
"""
import logging
from typing import Any, TypeVar, Optional
from .adapter import Adapter

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ApiAdapter(Adapter):
    def __init__(self, model_name: str, service_name: str, model: Optional[Any] = None, api_token: Optional[str] = None):
        super().__init__(model_name, service_name, model, api_token)

    def _is_available(self) -> bool:
        """Check if the API key is available."""
        available = bool(self.api_token and self.api_token.strip())
        if not available:
            logger.warning(f"{self.service_name} API key not found.")
        return available
