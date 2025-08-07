"""
Base adapter interfaces for AI models.
"""
from abc import ABC, abstractmethod
from typing import Optional


class ImageDescriptionAdapter(ABC):
    """Base interface for image description adapters."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the adapter is available."""
        pass

    @abstractmethod
    async def describe_image(self, image_url: str, prompt: Optional[str] = None) -> str:
        """
        Describe an image using the AI model.
        
        Args:
            image_url: URL of the image to describe
            prompt: Optional prompt to guide the description
            
        Returns:
            str: Description of the image
        """
        pass


class TextGenerationAdapter(ABC):
    """Base interface for text generation adapters."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the adapter is available."""
        pass

    @abstractmethod
    async def generate_text(self, text: str, prompt: str) -> str:
        """
        Generate text based on input text and prompt.
        
        Args:
            text: Input text to process
            prompt: Prompt to guide the generation
            
        Returns:
            str: Generated text
        """
        pass
