import logging
from typing import Optional
import google.generativeai as genai

from app.config import settings
from .base import ImageDescriptionAdapter

logger = logging.getLogger(__name__)


class GeminiAdapter(ImageDescriptionAdapter):
    def __init__(self):
        super().__init__(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_VISION_MODEL,  # e.g., "gemini-1.5-pro-vision-latest"
            service_name="Gemini"
        )
    
    def _init_model(self) -> None:
        """Initialize the Gemini model."""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    async def inference(self, image_url: str, prompt: Optional[str] = None) -> str:
        """Run inference with Gemini to describe an image."""
        logger.info(f"Gemini: describing image from {image_url}")

        try:
            final_prompt, image_data = await self.get_inputs(image_url, prompt)
            
            # Extract base64 data from the full data URL string
            # The format is usually "data:image/jpeg;base64,ACTUAL_DATA"
            if image_data.startswith('data:'):
                # Extract MIME type and base64 data
                parts = image_data.split(',', 1)
                if len(parts) == 2:
                    mime_type = parts[0].split(':')[1].split(';')[0]  # Extract mime type
                    base64_data = parts[1]  # Get only the base64 data
                else:
                    mime_type = "image/jpeg"
                    base64_data = image_data
            else:
                mime_type = "image/jpeg"
                base64_data = image_data
                
            logger.info(f"Gemini processing image with MIME type: {mime_type}")
                
            result_text = await self.run_inference(
                lambda: self.model.generate_content(
                    [
                        final_prompt,
                        {"mime_type": mime_type, "data": base64_data}
                    ],
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 1000,
                    },
                ).text
            )
            
            logger.info("Gemini model described image successfully")
            return result_text
        except Exception as e:
            logger.error(f"Gemini image description error: {e}")
            raise


