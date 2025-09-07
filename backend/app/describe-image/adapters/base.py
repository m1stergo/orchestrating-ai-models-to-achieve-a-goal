"""
Base adapter interfaces for AI models.
"""
from abc import ABC, abstractmethod
from typing import Any

from ..schemas import StandardResponse, ResponseDetails


class ImageDescriptionAdapter(ABC):
    """Base interface for image description adapters."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the adapter is available."""
        pass

    def format_response(self, status: str = "ERROR", id: str = None, 
                     detail_status: str = "ERROR", detail_message: str = "", 
                     detail_data: Any = "") -> StandardResponse:
        """
        Format a standard response object.
        
        Args:
            status: Overall status (COMPLETED, ERROR, IN_PROGRESS, etc.)
            id: Optional job ID for tracking
            detail_status: Status in details object (IDLE, ERROR, LOADING, COLD)
            detail_message: Message in details object
            detail_data: Data payload
            
        Returns:
            StandardResponse: Formatted standard response
        """
        return StandardResponse(
            status=status,
            id=id,
            details=ResponseDetails(
                status=detail_status,
                message=detail_message,
                data=detail_data
            )
        )
    
    def format_error(self, message: str, id: str = None) -> StandardResponse:
        """
        Format a standard error response.
        
        Args:
            message: Error message
            id: Optional job ID for tracking
            
        Returns:
            StandardResponse: Formatted error response
        """
        return self.format_response(
            status="ERROR",
            id=id,
            detail_status="ERROR",
            detail_message=message
        )
    
    @abstractmethod
    async def describe_image(self, image_url: str, prompt: str = None) -> StandardResponse:
        """
        Describe the image at the given URL, optionally using a prompt.
        Args:
            image_url: URL of the image to describe
            prompt: Optional prompt to guide the description
        Returns:
            StandardResponse: Description of the image in a standardized response format
        """
        pass

    @abstractmethod
    async def warmup(self) -> StandardResponse:
        """
        Warmup the adapter service for faster response times.
        Returns:
            StandardResponse: Warmup status in standardized format
        """
        pass

    @abstractmethod
    async def status(self, id: str = None) -> StandardResponse:
        """
        Check the health status of the adapter service.
        Args:
            id: Optional job ID to check status for
        Returns:
            StandardResponse: Health status in standardized format
        """
        pass
