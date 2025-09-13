from typing import Dict, Type, List
from .base import WebScrapingStrategy
from .alibaba import AlibabaScraper
from .aliexpress import AliExpressScraper
from .default import DefaultScraper
import logging

logger = logging.getLogger(__name__)


class ScraperFactory:
    """Factory class to create appropriate scraping scraper based on URL."""
    
    # Mapping of keywords to their corresponding scraper classes
    _scrapers: Dict[str, Type[WebScrapingStrategy]] = {
        "alibaba": AlibabaScraper,
        "aliexpress": AliExpressScraper,
        # Add more keyword mappings as needed
    }
    
    @classmethod
    def get_scraper(cls, url: str) -> WebScrapingStrategy:
        """
        Get the appropriate scraping scraper for the given URL.
        
        Args:
            url: The URL to determine scraper for
            
        Returns:
            WebScrapingStrategy: The appropriate scraper instance
        """
        try:
            # Convert URL to lowercase for case-insensitive matching
            url_lower = url.lower()
            
            # Check if URL contains any of our known keywords
            for keyword, scraper_class in cls._scrapers.items():
                if keyword in url_lower:
                    logger.info(f"Using {keyword} scraper for URL: {url}")
                    return scraper_class()
            
            # No specific scraper found, use default scraper
            logger.info(f"No specific scraper found for URL: {url}, using default scraper")
            return DefaultScraper()
            
        except Exception as e:
            logger.error(f"Error selecting scraper for URL {url}: {str(e)}")
            raise
    
    @classmethod
    def list_keys(cls) -> List[str]:
        """Get list of supported keywords."""
        return list(cls._scrapers.keys())
