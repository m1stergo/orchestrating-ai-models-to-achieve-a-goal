import logging
from bs4 import BeautifulSoup
from typing import List
from .base import WebScrapingStrategy

logger = logging.getLogger(__name__)

class DefaultScraper(WebScrapingStrategy):
    """Default scraper for general web content extraction."""
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from general web page."""
        # Try Open Graph title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]
        
        # Fallback to page title
        title_tag = soup.find("title")
        return title_tag.text.strip() if title_tag else ""
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract description from general web page."""
        # Try Open Graph description
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"]
        
        # Try meta description
        meta_desc = soup.find("meta", {"name": "description"})
        return meta_desc["content"] if meta_desc and meta_desc.get("content") else ""
    
    def extract_main_image(self, soup: BeautifulSoup) -> str:
        """Extract main image from general web page."""
        # Try Open Graph image
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]
        
        return ""
    
    def extract_media_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract media images from general web page."""
        media_images = []
        
        return media_images
