from PIL import Image
from io import BytesIO
import requests
from transformers import Qwen2_5_VLForConditionalGeneration
from qwen_vl_utils import process_vision_info
import torch
import logging
import time
import os
from .config import settings
from .s3_downloader import s3_downloader

logger = logging.getLogger(__name__)

class QwenModel:
    """ImageDescriptionModel for image description using model (local)."""

    def __init__(self, max_width: int = 512):
        self._model = None
        self._processor = None
        self.max_width = max_width

    def load_model(self):
        """Ensures that the model is loaded synchronously."""
        if self.is_loaded():
            return
            
        start_time = time.time()
        logger.info("Loading model... This may take several minutes.")
        model_name = settings.QWEN_MODEL_NAME

        # Try to ensure model is available locally (from S3 if needed)
        local_model_path = s3_downloader.ensure_model_local()
        
        # Use S3 downloaded model if available, otherwise use HuggingFace
        if local_model_path:
            model_name = local_model_path  # Use local path instead of HF model name
            logger.info(f"Using S3 downloaded model from: {local_model_path}")
        else:
            logger.info("Using HuggingFace model download")

        # Check if CUDA is available - REQUIRE GPU
        device_available = torch.cuda.is_available()
        logger.info(f"CUDA available: {device_available}")
        
        if not device_available:
            error_msg = "GPU is required for this service. No CUDA-compatible GPU detected. Terminating process."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        logger.info("Loading model with GPU acceleration...")
        logger.info("Starting model download and initialization...")
        try:
            # Configure model loading arguments
            model_kwargs = {
                "torch_dtype": "auto",
                "device_map": "auto",
                "trust_remote_code": True
            }
            
                
            self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_name,
                **model_kwargs
            )
        except Exception as e:
            logger.error(f"Failed to load model with GPU: {e}")
            raise RuntimeError(f"Failed to load model on GPU: {str(e)}")
            
        # Load processor too
        from transformers import AutoProcessor
        processor_kwargs = {"trust_remote_code": True}
            
        self._processor = AutoProcessor.from_pretrained(
            model_name, 
            **processor_kwargs
        )
        
        total_time = time.time() - start_time
        logger.info(f"Model loaded successfully and ready for inference - Total loading time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")

        return self._model, self._processor
    
    def is_loaded(self):
        """Check if model is loaded."""
        return self._model is not None and self._processor is not None
    
    def _download_and_resize_image(self, image_url: str) -> Image.Image:
        """Downloads the image and resizes it to max_width if necessary."""
        resp = requests.get(image_url)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert("RGB")

        if img.width > self.max_width:
            ratio = self.max_width / float(img.width)
            new_h = int(img.height * ratio)
            img = img.resize((self.max_width, new_h), Image.LANCZOS)

        return img

    def describe_image(self, image_url: str, prompt: str = None) -> str:
        logger.info(f"describing image from {image_url}")
        try:
            # Ensure model is loaded
            if not self.is_loaded():
                self.load_model()

            image = self._download_and_resize_image(image_url)

            if prompt is None:
                prompt = settings.PROMPT

            # Use PIL.Image (already resized) in message
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt},
                    ],
                }
            ]

            text = self._processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            image_inputs, video_inputs = process_vision_info(messages)

            inputs = self._processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            ).to(self._model.device)

            logger.info("Generating caption")
            generated_ids = self._model.generate(**inputs, max_new_tokens=256)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self._processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )

            description = output_text[0].strip() if output_text else "No description generated"
            logger.info("description generated successfully")
            return description

        except Exception as e:
            logger.error(f"error: {str(e)}")
            raise
