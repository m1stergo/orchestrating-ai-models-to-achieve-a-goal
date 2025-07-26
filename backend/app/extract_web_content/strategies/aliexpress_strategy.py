from typing import List
from bs4 import BeautifulSoup
from .base import WebScrapingStrategy


class AliExpressStrategy(WebScrapingStrategy):
    """Strategy for scraping AliExpress pages."""
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from AliExpress page."""
        # Try Open Graph title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]
        
        # Try product title specific to AliExpress
        product_title = soup.find("h1", {"class": "product-title-text"})
        if product_title:
            return product_title.text.strip()
        
        # Fallback to page title
        title_tag = soup.find("title")
        return title_tag.text.strip() if title_tag else ""
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract description from AliExpress page."""
        # Try Open Graph description
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"]
        
        # Try product description
        desc_div = soup.find("div", {"class": "product-description"})
        if desc_div:
            return desc_div.text.strip()
        
        # Try meta description
        meta_desc = soup.find("meta", {"name": "description"})
        return meta_desc["content"] if meta_desc and meta_desc.get("content") else ""
    
    def extract_main_image(self, soup: BeautifulSoup) -> str:
        """Extract main image from AliExpress page."""
        # Try Open Graph image
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]
        
        # Try AliExpress specific main image selector
        main_img = soup.find("img", {"class": "magnifier-image"})
        if main_img and main_img.get("src"):
            return main_img["src"]
        
        # Try another common selector
        main_img = soup.find("div", {"class": "image-view"})
        if main_img:
            img = main_img.find("img")
            if img and img.get("src"):
                return img["src"]
        
        return ""
    
    def extract_media_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract media images from AliExpress page."""
        media_images = []
        
        return media_images
