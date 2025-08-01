from app.extract_web_content.schemas import ExtractWebContentResponse
from app.extract_web_content.scrapers.factory import ScraperFactory


async def extract_web_content(url: str) -> ExtractWebContentResponse:
    """
    Extract content from a website using the appropriate extractor based on the URL.
    
    Args:
        url: The URL to extract content from
        
    Returns:
        ExtractWebContentResponse: The extracted content
    """
    # Get the appropriate extractor for this URL
    extractor = ScraperFactory.get_scraper(url)
    
    # Extract content using the extractor
    content = extractor.extract_content(url)
    
    return ExtractWebContentResponse(
        url=str(url),
        title=content["title"],
        description=content["description"],
        images=content["media_images"] if content["media_images"] else ([content["image_url"]] if content["image_url"] else [])
    )
