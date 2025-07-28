from fastapi import APIRouter, HTTPException
from schemas import ExtractWebContentRequest, ExtractWebContentResponse
from service import extract_web_content

router = APIRouter()


@router.post("/", response_model=ExtractWebContentResponse)
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
