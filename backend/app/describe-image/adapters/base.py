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
