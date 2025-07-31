import logging
from typing import List, Optional
from .base import BaseGenerateDescriptionStrategy
from .openai_strategy import OpenAIStrategy
from .gemini_strategy import GeminiStrategy
from .mistral_strategy import MistralStrategy

logger = logging.getLogger(__name__)


class GenerateDescriptionStrategyFactory:
    """Factory for managing text generation strategies."""
    
    def __init__(self):
        self.strategies = {
            "openai": OpenAIStrategy,
            "gemini": GeminiStrategy,
            "mistral": MistralStrategy
        }
        self._strategy_instances = {}
    
    def get_strategy(self, strategy_name: Optional[str] = None) -> BaseGenerateDescriptionStrategy:
        """
        Get a strategy instance by name or return the first available one.
        
        Args:
            strategy_name: Name of the strategy to get (optional)
            
        Returns:
            Strategy instance
            
        Raises:
            ValueError: If strategy not found or no strategies available
        """
        if strategy_name:
            if strategy_name not in self.strategies:
                available = list(self.strategies.keys())
                raise ValueError(f"Strategy '{strategy_name}' not found. Available: {available}")
            
            # Return cached instance or create new one
            if strategy_name not in self._strategy_instances:
                self._strategy_instances[strategy_name] = self.strategies[strategy_name]()
            
            return self._strategy_instances[strategy_name]
        
        raise ValueError("No text generation strategies available")
    
    async def get_available_strategies(self) -> List[dict]:
        """
        Get list of available strategies with their information.
        
        Returns:
            List of strategy information dictionaries
        """
        available_strategies = []
        
        for name, strategy_class in self.strategies.items():
            try:
                # Get or create strategy instance
                if name not in self._strategy_instances:
                    self._strategy_instances[name] = strategy_class()
                
                strategy = self._strategy_instances[name]
                
                # Check availability
                is_available = await strategy.is_available()
                
                # Get strategy info
                info = strategy.get_strategy_info()
                info["available"] = is_available
                
                available_strategies.append(info)
                
            except Exception as e:
                logger.error(f"Error checking strategy {name}: {str(e)}")
                available_strategies.append({
                    "name": name,
                    "available": False,
                    "error": str(e)
                })
        
        return available_strategies
    
    def list_strategy_names(self) -> List[str]:
        """Get list of all strategy names."""
        return list(self.strategies.keys())


# Global factory instance
strategy_factory = GenerateDescriptionStrategyFactory()
