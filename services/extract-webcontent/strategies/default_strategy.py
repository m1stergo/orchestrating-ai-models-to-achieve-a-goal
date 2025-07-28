from typing import List
from bs4 import BeautifulSoup
from .base import WebScrapingStrategy


class DefaultStrategy(WebScrapingStrategy):
    """Default strategy for scraping generic websites."""
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from generic page."""
        # Try Open Graph title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]
        
        # Try Twitter card title
        twitter_title = soup.find("meta", {"name": "twitter:title"})
        if twitter_title and twitter_title.get("content"):
            return twitter_title["content"]
        
        # Fallback to page title
        title_tag = soup.find("title")
        return title_tag.text.strip() if title_tag else ""
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract description from generic page."""
        # Try Open Graph description
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"]
        
        # Try Twitter card description
        twitter_desc = soup.find("meta", {"name": "twitter:description"})
        if twitter_desc and twitter_desc.get("content"):
            return twitter_desc["content"]
        
        # Try meta description
        meta_desc = soup.find("meta", {"name": "description"})
        return meta_desc["content"] if meta_desc and meta_desc.get("content") else ""
    
    def extract_main_image(self, soup: BeautifulSoup) -> str:
        """Extract main image from generic page."""
        # Try Open Graph image
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]
        
        # Try Twitter card image
        twitter_image = soup.find("meta", {"name": "twitter:image"})
        if twitter_image and twitter_image.get("content"):
            return twitter_image["content"]
        
        return ""
    
    def extract_media_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract media images from generic page."""
        media_images = ["https://via.placeholder.com/600x400"]
        return media_images
