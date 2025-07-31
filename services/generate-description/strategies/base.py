from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseGenerateDescriptionStrategy(ABC):
    """Abstract base class for text generation strategies."""
    
    def __init__(self):
        self.name = self.__class__.__name__.replace('Strategy', '').lower()
    
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
        Check if this strategy is available for use.
        
        Returns:
            True if the strategy can be used, False otherwise
        """
        pass
    
    @abstractmethod
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        Get information about this strategy.
        
        Returns:
            Dictionary containing strategy metadata
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()
