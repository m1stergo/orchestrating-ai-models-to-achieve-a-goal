from abc import ABC, abstractmethod
from schemas import DescribeImageResponse


class ImageDescriptionModel(ABC):
    """Abstract base class for image description models."""
    
    def __init__(self):
        self.model_name = self.__class__.__name__
    
    @abstractmethod
    async def describe_image(self, image_url: str, **kwargs) -> DescribeImageResponse:
        """
        Describe an image using the specific model.
        
        Args:
            image_url: URL of the image to describe
            **kwargs: Additional parameters specific to each model
            
        Returns:
            DescribeImageResponse: The image description result
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the model is available and properly configured.
        
        Returns:
            bool: True if the model can be used, False otherwise
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.model_name})"
    
    def __repr__(self) -> str:
        return self.__str__()
