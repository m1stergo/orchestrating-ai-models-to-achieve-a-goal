from typing import List
from bs4 import BeautifulSoup
from .base import WebScrapingStrategy


class AlibabaStrategy(WebScrapingStrategy):
    """Strategy for scraping Alibaba.com pages."""
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from Alibaba page."""
        # Try Open Graph title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]
        
        # Fallback to page title
        title_tag = soup.find("title")
        return title_tag.text.strip() if title_tag else ""
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract description from Alibaba page."""
        # Try Open Graph description
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"]
        
        # Try meta description
        meta_desc = soup.find("meta", {"name": "description"})
        return meta_desc["content"] if meta_desc and meta_desc.get("content") else ""
    
    def extract_main_image(self, soup: BeautifulSoup) -> str:
        """Extract main image from Alibaba page."""
        # Try Open Graph image
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]
        
        # Try to find product main image
        main_img = soup.find("img", {"class": "main-image"})
        if main_img and main_img.get("src"):
            return main_img["src"]
        
        return ""
    
    def extract_media_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract media images from Alibaba page."""
        media_images = []
        
        # Look for media images with specific test id (as in original code)
        for div in soup.find_all("div", {"data-testid": "media-image"}):
            img_tag = div.find("img")
            if img_tag and img_tag.get("src"):
                media_images.append(img_tag["src"])
        
        print(f"Total de imágenes extraídas: {len(media_images)}")
        return media_images
