"""
Base API adapter module for external AI service integration.

This module provides a base class for adapters that connect to external API services
such as OpenAI, Gemini, or other AI providers. It implements common functionality
for API authentication checking and extends the core Adapter interface.

Classes:
    ApiAdapter: Base adapter class for external API integrations
"""
import logging
from typing import Any, TypeVar, Optional
from .adapter import Adapter

# Configure module logger
logger = logging.getLogger(__name__)

# Generic type variable for return type flexibility
T = TypeVar('T')

class ApiAdapter(Adapter):
    """Base adapter for external API service integrations.
    
    This adapter class handles common functionality for connecting to external
    API services, particularly checking if the required API token is available.
    It serves as a base class for specific API implementations like OpenAI, Gemini, etc.
    
    Attributes:
        model_name (str): Name of the AI model being used
        service_name (str): Name of the service provider (e.g., "OpenAI", "Gemini")
        model (Any, optional): Instance of the model if locally loaded
        api_token (str, optional): Authentication token for API access
    """
    
    def __init__(self, model_name: str, service_name: str, model: Optional[Any] = None, api_token: Optional[str] = None):
        """Initialize the API adapter.
        
        Args:
            model_name: Name of the AI model to use
            service_name: Name of the service provider
            model: Optional instance of the model if loaded locally
            api_token: Optional API token for authentication
        """
        super().__init__(model_name, service_name, model, api_token)

    def _is_available(self) -> bool:
        """Check if the API key is available for this service.
        
        This method verifies that the API token is present and not empty,
        logging a warning if the token is missing.
        
        Returns:
            bool: True if the API token is available, False otherwise
        """
        available = bool(self.api_token and self.api_token.strip())
        if not available:
            logger.warning(f"{self.service_name} API key not found.")
        return available
