from app.extract_web_content.schemas import ExtractWebContentResponse


async def extract_web_content(url: str) -> ExtractWebContentResponse:
    """
    Mock function to extract content from a website.
    In a real implementation, this would use a library like requests, beautifulsoup, or scrapy.
    
    Args:
        url: The URL to extract content from
        
    Returns:
        ExtractWebContentResponse: The extracted content
    """
    # Mock response
    return ExtractWebContentResponse(
        url=str(url),
        title="Mock Website Title",
        keywords=["mock", "example", "extraction"],
        description="This is a mock description of the website.",
        images=["https://picsum.photos/200", "https://picsum.photos/200", "https://picsum.photos/200"]
    )
