from abc import ABC, abstractmethod
from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class WebScrapingStrategy(ABC):
    """Abstract base class for web scraping strategies."""
    
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    def get_soup(self, url: str) -> BeautifulSoup:
        """Common method to get BeautifulSoup object from URL."""
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, "lxml")
    
    def normalize_url(self, url: str, base_url: str) -> str:
        """Normalize URL to ensure it has proper protocol."""
        if not url:
            return ""
        
        # Handle protocol-relative URLs (//example.com/image.jpg)
        if url.startswith("//"):
            parsed_base = urlparse(base_url)
            return f"{parsed_base.scheme}:{url}"
        
        # Handle relative URLs
        if not url.startswith(("http://", "https://")):
            return urljoin(base_url, url)
        
        return url
    
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
        
        # Extract raw content
        raw_image_url = self.extract_main_image(soup)
        raw_media_images = self.extract_media_images(soup)
        
        # Normalize URLs
        normalized_image_url = self.normalize_url(raw_image_url, url)
        normalized_media_images = [self.normalize_url(img_url, url) for img_url in raw_media_images]
        
        return {
            "title": self.extract_title(soup),
            "description": self.extract_description(soup),
            "image_url": normalized_image_url,
            "media_images": normalized_media_images
        }
