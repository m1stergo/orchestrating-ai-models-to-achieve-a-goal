from abc import ABC, abstractmethod
from typing import Dict, Any
from schemas import DescribeImageResponse


class ImageDescriptionStrategy(ABC):
    """Abstract base class for image description strategies."""
    
    def __init__(self):
        self.strategy_name = self.__class__.__name__
    
    @abstractmethod
    async def describe_image(self, image_url: str, **kwargs) -> DescribeImageResponse:
        """
        Describe an image using the specific strategy.
        
        Args:
            image_url: URL of the image to describe
            **kwargs: Additional parameters specific to each strategy
            
        Returns:
            DescribeImageResponse: The image description result
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the strategy is available and properly configured.
        
        Returns:
            bool: True if the strategy can be used, False otherwise
        """
        pass
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        Get information about this strategy.
        
        Returns:
            Dict containing strategy metadata
        """
        return {
            "name": self.strategy_name,
            "available": self.is_available(),
            "type": "local" if "local" in self.strategy_name.lower() else "cloud"
        }
