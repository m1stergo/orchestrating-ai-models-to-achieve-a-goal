"""
OpenAI adapter for image description.
"""
import logging
import asyncio
import base64
import aiofiles
from typing import Optional
from urllib.parse import urlparse
from pathlib import Path
from openai import OpenAI
from app.config import settings
from .base import ImageDescriptionAdapter

logger = logging.getLogger(__name__)


class OpenAIAdapter(ImageDescriptionAdapter):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = settings.OPENAI_VISION_MODEL  # e.g., "gpt-4o"
        self.model = None

        if self.is_available():
            self.model = OpenAI(api_key=self.api_key)

    def is_available(self) -> bool:
        """Check if the OpenAI API key is available."""
        available = bool(self.api_key and self.api_key.strip())
        if not available:
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        return available

    async def describe_image(self, image_url: str, prompt: Optional[str] = None) -> str:
        """Describe an image using OpenAI's vision model."""
        logger.info(f"OpenAI: describing image from {image_url}")

        if not self.is_available():
            raise ValueError("OpenAI API key is not configured.")

        if prompt is None:
            prompt = "Describe this image in detail."

        try:
            # Always convert to base64 for better reliability
            image_data = await self._convert_image_to_base64(image_url)
            result_text = await asyncio.to_thread(self.describe_image_sync, image_data, prompt)
            
            logger.info("OpenAI model described image successfully")
            return result_text
        except Exception as e:
            logger.error(f"OpenAI image description error: {e}")
            raise

    async def _convert_image_to_base64(self, image_url: str) -> str:
        """Convert an image URL to base64 data URL."""
        try:
            parsed = urlparse(image_url)
            
            # Check if it's a remote URL (http/https)
            if parsed.scheme in ('http', 'https'):
                return await self._download_remote_image_to_base64(image_url)
            else:
                # Handle local file path
                return await self._convert_local_image_to_base64(image_url)
                
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            raise ValueError(f"Could not process image: {e}")

    async def _download_remote_image_to_base64(self, image_url: str) -> str:
        """Download remote image and convert to base64."""
        import aiohttp
        
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

    async def _convert_local_image_to_base64(self, image_url: str) -> str:
        """Convert local image file to base64."""
        # Extract the local file path from the URL
        parsed = urlparse(image_url)
        # Remove the leading slash and convert to local path
        relative_path = parsed.path.lstrip('/')
        
        # Construct the full path (assuming static files are served from app/static)
        base_path = Path(__file__).parent.parent.parent  # Go up to app/
        file_path = base_path / relative_path
        
        logger.info(f"Reading local image file: {file_path}")
        
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

    def describe_image_sync(self, image_data: str, prompt: str) -> str:
        """Describe image using base64 data."""
        if self.model is None:
            self.model = OpenAI(api_key=self.api_key)
            
        result = self.model.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data}}
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.7,
        )

        return result.choices[0].message.content or ""
