from abc import ABC, abstractmethod
from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup


class WebScrapingStrategy(ABC):
    """Abstract base class for web scraping strategies."""
    
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    def get_soup(self, url: str) -> BeautifulSoup:
        """Common method to get BeautifulSoup object from URL."""
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, "lxml")
    
    @abstractmethod
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from the page."""
        pass
    
    @abstractmethod
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract description from the page."""
        pass
    
    @abstractmethod
    def extract_main_image(self, soup: BeautifulSoup) -> str:
        """Extract main image URL from the page."""
        pass
    
    @abstractmethod
    def extract_media_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract media images from the page."""
        pass
    
    def extract_content(self, url: str) -> Dict[str, Any]:
        """Main method to extract all content using the strategy."""
        soup = self.get_soup(url)
        
        return {
            "title": self.extract_title(soup),
            "description": self.extract_description(soup),
            "image_url": self.extract_main_image(soup),
            "media_images": self.extract_media_images(soup)
        }
