from schemas import ExtractWebContentResponse
from strategies.factory import StrategyFactory


async def extract_web_content(url: str) -> ExtractWebContentResponse:
    """
    Extract content from a website using the appropriate strategy based on the URL.
    
    Args:
        url: The URL to extract content from
        
    Returns:
        ExtractWebContentResponse: The extracted content
    """
    # Get the appropriate strategy for this URL
    strategy = StrategyFactory.get_strategy(url)
    
    # Extract content using the strategy
    content = strategy.extract_content(url)
    
    return ExtractWebContentResponse(
        url=str(url),
        title=content["title"],
        description=content["description"],
        images=content["media_images"] if content["media_images"] else ([content["image_url"]] if content["image_url"] else [])
    )
