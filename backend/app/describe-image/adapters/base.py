"""
Base adapter interfaces for AI models.
"""
from abc import ABC, abstractmethod


class ImageDescriptionAdapter(ABC):
    """Base interface for image description adapters."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the adapter is available."""
        pass

    @abstractmethod
    async def describe_image(self, image_url: str, prompt: str = None) -> str:
        """
        Describe the image at the given URL, optionally using a prompt.
        Args:
            image_url: URL of the image to describe
            prompt: Optional prompt to guide the description
        Returns:
            str: Description of the image
        """
        pass

    @abstractmethod
    async def warmup(self) -> dict:
        """
        Warmup the adapter service for faster response times.
        Returns:
            dict: Warmup status and information
        """
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        """
        Check the health status of the adapter service.
        Returns:
            dict: Health status and information
        """
        pass
