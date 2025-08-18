"""
Base adapter interfaces for AI models.
"""
from abc import ABC, abstractmethod
from typing import Optional

# Shared prompt for e-commerce product description generation
ECOMMERCE_COPYWRITER_PROMPT = """You are a professional e-commerce copywriter. Write a clear and persuasive product description based strictly on the information below. Keep it concise and to the point, avoiding unnecessary fluff."""

# Shared prompt for promotional reel/TikTok script generation
REEL_PROMOTIONAL_PROMPT = """Create a short description for a Reels/TikTok promotional video.
The result should sound natural, conversational, and energetic, with short, punchy sentences that grab attention in the first few seconds.
Include a strong hook at the beginning, a simple middle part, and a call-to-action at the end.
Avoid being too formal, use common social media expressions, and keep the length suitable for a video under 30 seconds."""


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

    @abstractmethod
    async def generate_reel_script(self, text: str) -> str:
        """
        Generate a promotional reel/TikTok script from marketing text.
        
        Args:
            text: Input marketing text to transform
            
        Returns:
            str: Generated reel script
        """
        pass
