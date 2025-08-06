import logging
import requests
from pathlib import Path
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image

import google.generativeai as genai
from schemas import DescribeImageResponse
from .base import ImageDescriptionModel
from config import settings
import asyncio


logger = logging.getLogger(__name__)

class GeminiModel(ImageDescriptionModel):
    """Model for image description using Google Gemini SDK with image resize."""

    def __init__(self):
        super().__init__()
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL  # ej: "gemini-1.5-pro-latest"
        if self.is_available():
            genai.configure(api_key=self.api_key)

    def is_available(self) -> bool:
        available = bool(self.api_key and self.api_key.strip())
        if not available:
            logger.warning("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        return available

    def is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme in ("http", "https"), result.netloc])
        except Exception:
            return False

    def _download_and_resize_image(self, image_url: str, max_width: int = 512) -> tuple:
        """Download image, resize if wider than max_width, return (mime_type, bytes)."""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            mime_type = response.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()

            img = Image.open(BytesIO(response.content))

            if img.width > max_width:
                ratio = max_width / float(img.width)
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)

                # Convert to JPEG to ensure compatibility
                output = BytesIO()
                img.convert("RGB").save(output, format="JPEG", quality=90)
                return "image/jpeg", output.getvalue()

            return mime_type, response.content

        except Exception as e:
            logger.error(f"Error downloading or resizing image: {str(e)}")
            raise


    async def describe_image(self, image_url: str, prompt: str = None) -> DescribeImageResponse:
        return await asyncio.to_thread(self._describe_image_sync, image_url, prompt)

    def _describe_image_sync(self, image_url: str, prompt: str = None) -> DescribeImageResponse:
        """Describe image using Google Gemini API via SDK."""
        logger.info(f"GeminiModel: describing image from {image_url}")

        if not self.is_available():
            raise ValueError("Gemini API key is not configured.")

        if not self.is_valid_url(image_url):
            raise ValueError("Invalid image URL")

        if prompt is None:
            PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "default.txt"
            prompt = PROMPT_PATH.read_text(encoding="utf-8")

        try:
            mime_type, image_data = self._download_and_resize_image(image_url, max_width=512)

            model = genai.GenerativeModel(self.model_name)
            result = model.generate_content(
                [prompt, {"mime_type": mime_type, "data": image_data}],
                generation_config={"max_output_tokens": 500}
            )

            # Log finish reason
            if hasattr(result, "candidates") and result.candidates:
                finish_reason = getattr(result.candidates[0], "finish_reason", None)
                if finish_reason and finish_reason != "STOP":
                    logger.warning(f"Generation stopped: {finish_reason}")

            description = result.text.strip() if result.text else "No response generated"
            logger.info("GeminiModel: description generated successfully")
            return DescribeImageResponse(description=description)

        except Exception as e:
            logger.error(f"GeminiModel error: {str(e)}")
            raise
