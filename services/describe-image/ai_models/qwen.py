from PIL import Image
from io import BytesIO
import requests
from transformers import (
    AutoProcessor,
    Qwen2_5_VLForConditionalGeneration
)
from qwen_vl_utils import process_vision_info
import torch
from schemas import DescribeImageResponse
from .base import ImageDescriptionModel
import logging

logger = logging.getLogger(__name__)


class QwenModel(ImageDescriptionModel):
    """ModelImageDescriptionModel for image description using Qwen2.5-VL model (local)."""
    
    def __init__(self):
        super().__init__()
        self._model = None
        self._processor = None
    
    def is_available(self) -> bool:
        """Check if Qwen model dependencies are available."""
        try:
            # Check if we can import required modules
            from transformers import Qwen2_5_VLForConditionalGeneration
            from qwen_vl_utils import process_vision_info
            return True
        except ImportError:
            return False
    
    def _load_qwen_model(self):
        """Load Qwen model and processor if not already loaded."""
        if self._model is None or self._processor is None:
            logger.info("Loading Qwen2.5-VL model...")
            
            # Load the model and processor
            model_name = "Qwen/Qwen2.5-VL-7B-Instruct"

            self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.bfloat16,
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                max_memory={0: "14GB", "cpu": "8GB"}  # RTX 5070 Ti 16GB + 16GB RAM optimized
            )
            self._processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
            
            logger.info("Qwen2.5-VL model loaded successfully")
        
        return self._model, self._processor
    
    async def describe_image(self, image_url: str, prompt: str = None, **kwargs) -> DescribeImageResponse:
        """Describe image using Qwen2.5-VL model."""
        logger.info(f"QwenModel: describing image from {image_url}")
        
        try:
            # Load model if needed
            model, processor = self._load_qwen_model()
            
            # Generate caption
            description = self._get_qwen_caption(image_url, prompt, model, processor)
            
            response = DescribeImageResponse(description=description)
            logger.info("QwenModel: description generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"QwenModel error: {str(e)}")
            raise
    
    def _get_qwen_caption(self, image_url: str, prompt, model, processor) -> str:
        """Generate caption using Qwen model."""
        logger.info(f"Processing image from URL: {image_url}")
        
        # Load and convert image
        image = Image.open(BytesIO(requests.get(image_url).content)).convert("RGB")
        logger.info(f"Image loaded successfully, size: {image.size}")
        
        if prompt is None:
            from pathlib import Path
            PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "default.txt"
            prompt = PROMPT_PATH.read_text(encoding="utf-8")

        # Prepare messages in the format expected by Qwen2.5-VL
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image_url,
                    },
                    {
                        "type": "text", 
                        "text": prompt
                    }
                ],
            }
        ]
        
        # Preparation for inference
        text = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to(model.device)
        
        # Generate the response
        logger.info("Generating caption with Qwen2.5-VL...")
        generated_ids = model.generate(**inputs, max_new_tokens=256)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        
        response = output_text[0] if output_text else "No description generated"
        logger.info("Caption generated successfully")
        return response

