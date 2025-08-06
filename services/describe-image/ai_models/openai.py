from openai import OpenAI
from schemas import DescribeImageResponse
from pathlib import Path
from urllib.parse import urlparse
from config import settings
from .base import ImageDescriptionModel
import logging
import asyncio
import requests
from io import BytesIO
from PIL import Image
import base64

logger = logging.getLogger(__name__)

class OpenAIVisionModel(ImageDescriptionModel):
    """Model for image description using OpenAI Vision with pre-resize."""

    def __init__(self):
        super().__init__()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_width = 512  # podés hacerlo configurable si querés

    def is_available(self) -> bool:
        available = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())
        if not available:
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        return available

    def is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme in ("http", "https"), result.netloc])
        except Exception:
            return False

    async def describe_image(self, image_url: str, prompt: str = None) -> DescribeImageResponse:
        # Mantengo tu interfaz async llamando a la versión sync
        return await asyncio.to_thread(self._describe_image_sync, image_url, prompt)

    def _download_and_resize_to_data_url(self, image_url: str) -> str:
        """
        Descarga la imagen, redimensiona a max_width si hace falta,
        y devuelve una data URL base64 lista para el campo image_url.url.
        """
        resp = requests.get(image_url)
        resp.raise_for_status()
        mime = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
        content = resp.content

        img = Image.open(BytesIO(content))

        # Si es más ancha que max_width, redimensiona y convierte a JPEG
        if img.width > self.max_width:
            ratio = self.max_width / float(img.width)
            new_h = int(img.height * ratio)
            img = img.resize((self.max_width, new_h), Image.LANCZOS)
            buf = BytesIO()
            img.convert("RGB").save(buf, format="JPEG", quality=90)
            mime = "image/jpeg"
            data = buf.getvalue()
        else:
            # Si no se redimensiona, usa tal cual
            data = content

        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    def _describe_image_sync(self, image_url: str, prompt: str = None) -> DescribeImageResponse:
        logger.info(f"Describing image from {image_url}")

        if not self.is_available():
            raise ValueError("OpenAI API key is not configured.")

        if not self.is_valid_url(image_url):
            raise ValueError("Invalid image URL")

        if prompt is None:
            PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "default.txt"
            prompt = PROMPT_PATH.read_text(encoding="utf-8")

        try:
            data_url = self._download_and_resize_to_data_url(image_url)

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": data_url,
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )

            description = completion.choices[0].message.content
            logger.info("Description generated successfully")
            return DescribeImageResponse(description=description)

        except Exception as e:
            logger.error(f"OpenAIVisionModel error: {str(e)}")
            raise
