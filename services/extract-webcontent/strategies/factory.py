from typing import Dict, Type
from .base import WebScrapingStrategy
from .alibaba_strategy import AlibabaStrategy
from .aliexpress_strategy import AliExpressStrategy
from .default_strategy import DefaultStrategy


class StrategyFactory:
    """Factory class to create appropriate scraping strategy based on URL."""
    
    # Mapping of keywords to their corresponding strategy classes
    _strategies: Dict[str, Type[WebScrapingStrategy]] = {
        "alibaba": AlibabaStrategy,
        "aliexpress": AliExpressStrategy,
        # Add more keyword mappings as needed
    }
    
    @classmethod
    def get_strategy(cls, url: str) -> WebScrapingStrategy:
        """
        Get the appropriate scraping strategy for the given URL.
        
        Args:
            url: The URL to determine strategy for
            
        Returns:
            WebScrapingStrategy: The appropriate strategy instance
        """
        try:
            # Convert URL to lowercase for case-insensitive matching
            url_lower = url.lower()
            
            # Check if URL contains any of our known keywords
            for keyword, strategy_class in cls._strategies.items():
                if keyword in url_lower:
                    return strategy_class()
            
            # Default strategy for unknown URLs
            return DefaultStrategy()
            
        except Exception:
            # If any error occurs, use default strategy
            return DefaultStrategy()
    
    @classmethod
    def get_supported_keywords(cls) -> list:
        """Get list of supported keywords."""
        return list(cls._strategies.keys())
