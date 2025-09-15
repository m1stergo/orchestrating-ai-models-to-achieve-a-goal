"""
Utility functions for image processing in adapters.
"""
import logging
import base64
import aiofiles
from urllib.parse import urlparse
from pathlib import Path
import aiohttp
from typing import Optional


logger = logging.getLogger(__name__)

"""
Shared prompts for image description services.
"""

def get_image_description_prompt(custom_prompt: Optional[str] = None) -> str:
    """
    Get image description prompt template.
    
    Args:
        custom_prompt: Optional custom prompt from user settings
        
    Returns:
        str: The prompt template
    """
    if custom_prompt and custom_prompt.strip():
        return custom_prompt
        
    return """Analyze the main product in the image provided. Focus exclusively on the product itself. Based on your visual analysis of the product, complete the following template:

Image description: A brief but comprehensive visual description of the item, detailing its color, shape, material, and texture.
Product type: What is the object?
Material: What is it made of? Be specific if possible (e.g., "leather," "plastic," "wood").
Keywords: List relevant keywords that describe the item's appearance or function."""



async def convert_image_to_base64(image_url: str) -> str:
    """Convert an image URL to base64 data URL.
    
    Args:
        image_url: URL or path to the image
        
    Returns:
        str: Base64 encoded data URL
    """
    try:
        parsed = urlparse(image_url)
        
        # Check if it's a remote URL (http/https)
        if parsed.scheme in ('http', 'https'):
            return await download_remote_image_to_base64(image_url)
        else:
            # Handle local file path
            return await convert_local_image_to_base64(image_url)
            
    except Exception as e:
        logger.error(f"Error converting image to base64: {e}")
        raise ValueError(f"Could not process image: {e}")


async def download_remote_image_to_base64(image_url: str) -> str:
    """Download remote image and convert to base64.
    
    Args:
        image_url: URL of the remote image
        
    Returns:
        str: Base64 encoded data URL
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    timeout = aiohttp.ClientTimeout(total=30)
    connector = aiohttp.TCPConnector(ssl=False)  # Skip SSL verification
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector, headers=headers) as session:
        async with session.get(image_url) as response:
            if response.status != 200:
                raise ValueError(f"Failed to download image: HTTP {response.status}")
            
            image_data = await response.read()
            
            # Encode to base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # Determine MIME type from Content-Type header or URL extension
            content_type = response.headers.get('Content-Type', '')
            if content_type.startswith('image/'):
                mime_type = content_type
            else:
                # Fallback to extension-based detection
                extension = Path(urlparse(image_url).path).suffix.lower()
                mime_type = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg', 
                    '.png': 'image/png',
                    '.webp': 'image/webp',
                    '.gif': 'image/gif'
                }.get(extension, 'image/jpeg')
            
            return f"data:{mime_type};base64,{base64_data}"


async def convert_local_image_to_base64(image_url: str) -> str:
    """Convert local image file to base64.
    
    Args:
        image_url: URL or path to the local image
        
    Returns:
        str: Base64 encoded data URL
    """
    # Extract the local file path from the URL
    parsed = urlparse(image_url)
    # Remove the leading slash and convert to local path
    relative_path = parsed.path.lstrip('/')
    
    # Construct the full path (assuming static files are served from app/static)
    base_path = Path(__file__).parent.parent.parent  # Go up to app/
    file_path = base_path / relative_path
    
    logger.info(f"===== Reading local image file: {file_path} =====")
    
    # Read the file asynchronously
    async with aiofiles.open(file_path, 'rb') as f:
        image_data = await f.read()
    
    # Encode to base64
    base64_data = base64.b64encode(image_data).decode('utf-8')
    
    # Determine MIME type based on file extension
    extension = file_path.suffix.lower()
    mime_type = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg', 
        '.png': 'image/png',
        '.webp': 'image/webp',
        '.gif': 'image/gif'
    }.get(extension, 'image/jpeg')
    
    return f"data:{mime_type};base64,{base64_data}"
