import logging
from typing import Optional
import google.generativeai as genai

from app.config import settings
from app.shared.api_adapter import ApiAdapter
from app.shared.schemas import ServiceResponse
from ..shared.prompts import get_image_description_prompt
from ..shared.utils import convert_image_to_base64


logger = logging.getLogger(__name__)


class GeminiAdapter(ApiAdapter):
    def __init__(self):
        super().__init__(
            api_token=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_VISION_MODEL,  # e.g., "gemini-1.5-pro-vision-latest"
            service_name="Gemini"
        )
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    async def infer(self, image_url: str, prompt: Optional[str] = None) -> ServiceResponse:
        logger.info(f"===== Gemini: describing image from {image_url} =====")
            
        final_prompt = get_image_description_prompt(prompt)
        image_data = await convert_image_to_base64(image_url)
        
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
            
        logger.info(f"===== Gemini processing image with MIME type: {mime_type} =====")
            
        response = await self.run(
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
        
        return response


