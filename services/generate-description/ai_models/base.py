from abc import ABC, abstractmethod

class BaseGenerateDescriptionModel(ABC):
    """Abstract base class for text generation models."""
    
    def __init__(self):
        self.name = self.__class__.__name__.replace('Model', '').lower()
    
    @abstractmethod
    async def generate_description(self, text: str, prompt: str) -> str:
        """
        Generate a description based on the input text and prompt.
        
        Args:
            text: The input text to process
            prompt: The prompt/instruction for generation
            
        Returns:
            Generated description text
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this model is available for use.
        
        Returns:
            True if the model can be used, False otherwise
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()
