from typing import Dict, Type, Optional
from .base import ImageDescriptionStrategy
from .qwen_strategy import QwenStrategy
from .openai_strategy import OpenAIVisionStrategy
from .gemini_strategy import GeminiStrategy
import logging

logger = logging.getLogger(__name__)


class ImageDescriptionStrategyFactory:
    """Factory class to create appropriate image description strategy."""
    
    # Available strategies
    _strategies: Dict[str, Type[ImageDescriptionStrategy]] = {
        "qwen": QwenStrategy,
        "openai": OpenAIVisionStrategy,
        "gemini": GeminiStrategy,
    }
    
    # Default strategy preference order
    _default_preference = ["openai", "gemini", "qwen"]
    
    @classmethod
    def get_strategy(cls, preferred_strategy: Optional[str] = None) -> ImageDescriptionStrategy:
        """
        Get the appropriate image description strategy.
        
        Args:
            preferred_strategy: The preferred strategy name (e.g., "qwen", "openai")
                               If None, will use the first available strategy from default preference
        
        Returns:
            ImageDescriptionStrategy: The strategy instance
        
        Raises:
            ValueError: If no strategy is available or preferred strategy is invalid
        """
        try:
            # If a specific strategy is requested
            if preferred_strategy:
                if preferred_strategy not in cls._strategies:
                    available = list(cls._strategies.keys())
                    raise ValueError(f"Unknown strategy '{preferred_strategy}'. Available: {available}")
                
                strategy_class = cls._strategies[preferred_strategy]
                strategy = strategy_class()
                
                if strategy.is_available():
                    logger.info(f"✅ Using requested strategy: {preferred_strategy}")
                    return strategy
                else:
                    logger.warning(f"⚠️ Requested strategy '{preferred_strategy}' is not available, falling back to default")
            
            # Fall back to first available strategy from preference list
            for strategy_name in cls._default_preference:
                if strategy_name in cls._strategies:
                    strategy_class = cls._strategies[strategy_name]
                    strategy = strategy_class()
                    
                    if strategy.is_available():
                        logger.info(f"✅ Using fallback strategy: {strategy_name}")
                        return strategy
                    else:
                        logger.warning(f"⚠️ Strategy '{strategy_name}' is not available")
            
            # If no strategy is available
            raise ValueError("No image description strategy is available. Please check your configuration.")
            
        except Exception as e:
            logger.error(f"❌ Error creating strategy: {str(e)}")
            raise
    
    @classmethod
    def get_available_strategies(cls) -> Dict[str, Dict]:
        """
        Get information about all available strategies.
        
        Returns:
            Dict with strategy names and their availability info
        """
        strategies_info = {}
        
        for name, strategy_class in cls._strategies.items():
            try:
                strategy = strategy_class()
                strategies_info[name] = strategy.get_strategy_info()
            except Exception as e:
                strategies_info[name] = {
                    "name": name,
                    "available": False,
                    "error": str(e)
                }
        
        return strategies_info
    
    @classmethod
    def add_strategy(cls, name: str, strategy_class: Type[ImageDescriptionStrategy]):
        """
        Add a new strategy to the factory.
        
        Args:
            name: Strategy name
            strategy_class: Strategy class
        """
        cls._strategies[name] = strategy_class
        logger.info(f"✅ Added new strategy: {name}")
    
    @classmethod
    def set_default_preference(cls, preference_order: list):
        """
        Set the default strategy preference order.
        
        Args:
            preference_order: List of strategy names in preference order
        """
        cls._default_preference = preference_order
        logger.info(f"✅ Updated default preference order: {preference_order}")
