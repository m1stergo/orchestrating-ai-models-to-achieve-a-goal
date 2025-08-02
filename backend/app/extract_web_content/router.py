from fastapi import APIRouter, HTTPException
from app.extract_web_content.schemas import ExtractWebContentRequest, ExtractWebContentResponse
from app.extract_web_content.service import extract_web_content

router = APIRouter()


@router.post(
    "/",
    response_model=ExtractWebContentResponse,
    summary="Extract Web Content",
    description="""
    Extract and parse content from web pages using internal scraping service.
    
    This endpoint uses an internal web scraping service to extract structured content
    from web pages. It supports multiple e-commerce platforms and general web content.
    
    **Supported Platforms:**
    - AliExpress product pages
    - Alibaba product pages
    - General web content
    
    **Input Requirements:**
    - `url`: Valid HTTP/HTTPS URL to extract content from
    """
)
async def extract_site_content_endpoint(request: ExtractWebContentRequest):
    """
    Endpoint to extract content from a website.
    
    Args:
        request: The request containing the URL to extract content from
        
    Returns:
        The extracted content
    """
    try:
        result = await extract_web_content(request.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract web content: {str(e)}")
