"""
Base adapter interfaces for AI models.
"""
from abc import ABC, abstractmethod

from typing import Tuple, Optional
from ..shared.utils import convert_image_to_base64, get_image_description_prompt
from abc import ABC, abstractmethod
from app.shared.api_adapter import ApiAdapter

class ImageDescriptionAdapter(ApiAdapter, ABC):
    async def get_inputs(self, image_url: str, prompt: Optional[str] = None) -> Tuple[str, str]:
        final_prompt = get_image_description_prompt(prompt)
        image_data = await convert_image_to_base64(image_url)

        return final_prompt, image_data

    @abstractmethod
    async def inference(self, image_url: str, prompt: Optional[str] = None) -> str:
        """Run inference with the model to describe an image."""
        raise NotImplementedError
    

        
