from app.extract_web_content.schemas import ExtractWebContentResponse
from app.extract_web_content.scrapers.factory import ScraperFactory
from pydantic import HttpUrl
from typing import Union

async def extract_web_content(url: Union[str, HttpUrl]) -> ExtractWebContentResponse:
    """
    Extract content from a website using the appropriate extractor based on the URL.
    
    Args:
        url: The URL to extract content from
        
    Returns:
        ExtractWebContentResponse: The extracted content
    """
    # Convert HttpUrl to string if needed
    url_str = str(url)
    
    # Get the appropriate extractor for this URL
    extractor = ScraperFactory.get_scraper(url_str)
    
    # Extract content using the extractor
    content = extractor.extract_content(url_str)
    
    return ExtractWebContentResponse(
        url=url_str,
        title=content["title"],
        description=content["description"],
        images=content["media_images"] if content["media_images"] else ([content["image_url"]] if content["image_url"] else [])
    )
