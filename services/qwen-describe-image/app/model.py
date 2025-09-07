from PIL import Image
from io import BytesIO
import requests
from transformers import Qwen2_5_VLForConditionalGeneration
from qwen_vl_utils import process_vision_info
import torch
import logging
import time
import os
from enum import Enum
from .config import settings

logger = logging.getLogger(__name__)

class ModelState(Enum):
    COLD = "COLD"
    LOADING = "LOADING"
    IDLE = "IDLE"
    ERROR = "ERROR"

class QwenModel:
    """ImageDescriptionModel for image description using model (local)."""
    def __init__(self, max_width: int = 512):
        self._model = None
        self._processor = None
        self.max_width = max_width
        self._state = ModelState.COLD
        self._loading_start_time = None
        self._error_message = None

    def load_model(self):
        """Ensures that the model is loaded synchronously."""
        if self.is_loaded():
            self._state = ModelState.IDLE
            return
            
        self._state = ModelState.LOADING
        self._loading_start_time = time.time()
        self._error_message = None
        
        start_time = time.time()
        logger.info("======== Qwen model loading... This may take several minutes. ========")
        model_name = settings.QWEN_MODEL_NAME

        # Set HuggingFace cache directory if specified
        if settings.HUGGINGFACE_CACHE_DIR:
            cache_dir = settings.HUGGINGFACE_CACHE_DIR
            os.environ['TRANSFORMERS_CACHE'] = cache_dir
            os.environ['HF_HOME'] = cache_dir
            logger.info(f"======== Using custom HuggingFace cache directory: {cache_dir} ========")
        else:
            logger.info("======== Using default HuggingFace cache directory ========")

        # Check if CUDA is available - REQUIRE GPU
        device_available = torch.cuda.is_available()
        logger.info(f"======== CUDA available: {device_available} ========")
        
        if not device_available:
            error_msg = "GPU is required for this service. No CUDA-compatible GPU detected. Terminating process."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        logger.info("======== Starting model download and initialization... ========")
        try:
            # Pass cache_dir to from_pretrained if specified
            model_kwargs = {
                "torch_dtype": "auto",
                "device_map": "auto",
                "trust_remote_code": True
            }
            if settings.HUGGINGFACE_CACHE_DIR:
                model_kwargs["cache_dir"] = settings.HUGGINGFACE_CACHE_DIR
                
            self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_name,
                **model_kwargs
            )
        except Exception as e:
            logger.error(f"======== Failed to load model with GPU: {e} ========")
            self._state = ModelState.ERROR
            self._error_message = str(e)
            raise RuntimeError(f"Failed to load model on GPU: {str(e)}")
            
        # Load processor too
        try:
            from transformers import AutoProcessor
            processor_kwargs = {"trust_remote_code": True}
            if settings.HUGGINGFACE_CACHE_DIR:
                processor_kwargs["cache_dir"] = settings.HUGGINGFACE_CACHE_DIR
                
            self._processor = AutoProcessor.from_pretrained(
                model_name, 
                **processor_kwargs
            )
            
            # Successfully loaded both model and processor
            self._state = ModelState.IDLE
            total_time = time.time() - start_time
            logger.info(f"======== Model loaded successfully and ready for inference - Total loading time: {total_time:.2f} seconds ({total_time/60:.2f} minutes) ========")

            return self._model, self._processor
            
        except Exception as e:
            logger.error(f"======== Failed to load processor: {e} ========")
            self._state = ModelState.ERROR
            self._error_message = str(e)
            raise RuntimeError(f"Failed to load processor: {str(e)}")
    
    def is_loaded(self):
        """Check if model is loaded."""
        return self._model is not None and self._processor is not None
    
    @property
    def state(self) -> ModelState:
        """Get current model state."""
        return self._state
    
    @property
    def error_message(self) -> str:
        """Get error message if state is ERROR."""
        return self._error_message
    
    @property
    def loading_start_time(self) -> float:
        """Get loading start time."""
        return self._loading_start_time
    
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
        logger.info(f"======== Describing image from {image_url} ========")
        try:
            # Ensure model is loaded
            if not self.is_loaded():
                self.load_model()

            image = self._download_and_resize_image(image_url)

            prompt = settings.PROMPT if prompt is None else prompt

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

            logger.info("======== Generating caption ========")
            generated_ids = self._model.generate(**inputs, max_new_tokens=256)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self._processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )

            description = output_text[0].strip() if output_text else "No description generated"
            logger.info("======== Description generated successfully ========")
            return description

        except Exception as e:
            logger.error(f"======== Error: {str(e)} ========")
            raise
