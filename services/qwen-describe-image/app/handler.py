"""Qwen Vision-Language Model handler implementation.

This module provides the QwenHandler class that implements the InferenceHandler
interface for the Qwen vision-language model. It handles model loading, image processing,
and running inference to generate descriptions from images.

The handler supports downloading the model from HuggingFace, preprocessing images,
and generating captions based on prompts.
"""

from PIL import Image
from io import BytesIO
import requests
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import logging
import time
from typing import Dict, Any
from huggingface_hub import snapshot_download
import os
from .config import settings
from .common import InferenceHandler, InferenceResponse, InferenceStatus

# Configure module logger
logger = logging.getLogger(__name__)

class QwenHandler(InferenceHandler):
    """Handler for Qwen vision-language model inference.
    
    This class implements the InferenceHandler interface for the Qwen
    vision-language model. It handles model loading, image processing,
    and running inference to generate descriptions from images.
    
    Attributes:
        model_name: Name or path of the Qwen model to use
        _processor: Text processor for tokenization and encoding
        max_width: Maximum width to resize images to before processing
    """
    
    def __init__(self, model_name: str, max_width: int = 512):
        """Initialize the Qwen handler.
        
        Args:
            model_name: Name or path of the Qwen model to use
            max_width: Maximum width to resize images to (default: 512px)
        """
        super().__init__(model_name)
        self._processor = None
        self.max_width = max_width

    def _materialize_model(self) -> str:
        """Download and prepare the model files.
        
        This method downloads the model from HuggingFace Hub if not available
        locally, using the configured cache and local directories. It filters
        the files to download only necessary model components and not documentation
        or example files.
        
        Returns:
            str: Path to the downloaded/cached model directory
            
        Note:
            This uses HuggingFace's snapshot_download to efficiently download
            and cache model files, with resume capability for large models.
        """
        # Use the centralized Pydantic configuration
        base_models_dir = settings.MODELS_DIR
        local_dir = f"{base_models_dir}/{self.model_name.replace('/', '__')}"
        os.makedirs(local_dir, exist_ok=True)
        cache_dir = settings.HUGGINGFACE_CACHE_DIR
        
        logger.info(f"==== snapshot_download to {local_dir} (cache: {cache_dir}) ====")
        
        # Download model files, filtering unnecessary files
        path = snapshot_download(
            repo_id=self.model_name,
            cache_dir=cache_dir,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
            # Only download model files, not documentation or examples
            allow_patterns=["*.safetensors","*.bin","*.json","tokenizer.*","processor.*","*.model","vocab.*","merges.txt",".gitattributes"],
            ignore_patterns=["images/*","assets/*","examples/*","docs/*","test*/*","*.md"],
        )
        return path

    def _do_load_model(self) -> InferenceResponse:
        """Load the Qwen vision-language model into memory.
        
        This method implements the abstract method from InferenceHandler.
        It downloads the model if needed, then loads it with optimal settings
        for memory management and GPU utilization.
        
        Returns:
            InferenceResponse: Response with status of the model loading operation
            
        Note:
            This is a resource-intensive operation that may take several minutes
            depending on the model size and hardware configuration.
        """
        try:
            logger.info("==== Loading model... This may take several minutes. ====")

            # Download model files if needed
            local_repo = self._materialize_model()

            # Configure model loading parameters for optimal performance
            model_kwargs = {
                "trust_remote_code": True,  # Required for Qwen models
                "device_map": "auto",      # Automatically determine device placement
                "low_cpu_mem_usage": True, # Optimize CPU memory usage during loading
                "offload_folder": "/runpod-volume/offload", # Folder for weight offloading
                "torch_dtype": "auto",    # Automatically select precision
                # Memory limits for GPU and CPU
                "max_memory": {0: settings.QWEN_MAX_MEMORY_GPU, "cpu": settings.QWEN_MAX_MEMORY_CPU},
            }

            # Load the model and processor
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(local_repo, **model_kwargs)
            self._processor = AutoProcessor.from_pretrained(local_repo, trust_remote_code=True)

            # Update status and log success
            self.status = InferenceStatus.COMPLETED
            total_time = time.time() - self.loading_start_time
            logger.info(f"==== Model loaded successfully and ready for inference - {total_time:.2f}s ({total_time/60:.2f}m) ====")
            return InferenceResponse(status=InferenceStatus.COMPLETED, message="Model is ready to use.")

        except Exception as e:
            # Handle errors during model loading
            logger.error(f"==== Failed to load model: {e} ====")
            self.status = InferenceStatus.FAILED
            self.error_message = str(e)
            return InferenceResponse(status=InferenceStatus.FAILED, message=f"Failed to load model: {e}")

    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready for inference.
        
        This method implements the abstract method from InferenceHandler.
        It verifies that both the model and processor are loaded.
        
        Returns:
            bool: True if the model and processor are loaded, False otherwise
        """
        return self.model is not None and self._processor is not None

    def _download_and_resize_image(self, image_url: str) -> Image.Image:
        """Download an image from a URL and resize if needed.
        
        This method downloads an image from a URL, converts it to RGB format,
        and resizes it if it exceeds the maximum width while maintaining
        the aspect ratio.
        
        Args:
            image_url: URL of the image to download
            
        Returns:
            Image.Image: Processed PIL Image object
            
        Raises:
            requests.HTTPError: If the image download fails
        """
        # Download the image
        resp = requests.get(image_url)
        resp.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        # Open image and convert to RGB
        img = Image.open(BytesIO(resp.content)).convert("RGB")
        
        # Resize if needed while maintaining aspect ratio
        if img.width > self.max_width:
            ratio = self.max_width / float(img.width)
            img = img.resize((self.max_width, int(img.height * ratio)), Image.LANCZOS)
            
        return img

    def infer(self, request_data: Dict[str, Any]) -> InferenceResponse:
        """Run inference on an image to generate a description.
        
        This method implements the abstract method from InferenceHandler.
        It processes the input image, runs it through the Qwen model with
        the specified prompt, and returns the generated description.
        
        Args:
            request_data: Dictionary with inference parameters including:
                - image_url: URL of the image to describe (required)
                - prompt: Custom prompt to use (optional)
                
        Returns:
            InferenceResponse: Response with the generated description
            
        Note:
            If the model is not loaded, this will trigger model loading
            and return a warming up status.
        """
        try:
            # Extract and validate image URL
            image_url = request_data.get('image_url')
            if not image_url:
                raise ValueError("The 'image_url' parameter is required for this model")
            logger.info(f"==== Describing image from {image_url} ====")

            # Check if model is loaded, if not start loading and return warming up status
            if not self.is_loaded():
                self.load_model()
                return InferenceResponse(
                    status=InferenceStatus.WARMINGUP, 
                    message="Model is warming up..."
                )

            # Process the image
            image = self._download_and_resize_image(image_url)
            
            # Get prompt from request or use default
            prompt = request_data.get('prompt', settings.PROMPT)
            
            # Format input in the chat template format for Qwen
            messages = [
                {"role": "user", "content": [
                    {"type": "image", "image": image}, 
                    {"type": "text", "text": prompt}
                ]}
            ]

            # Prepare inputs for the model
            text = self._processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self._processor(
                text=[text], 
                images=image_inputs, 
                videos=video_inputs, 
                padding=True, 
                return_tensors="pt"
            ).to(self.model.device)

            # Generate description
            logger.info("==== Generating caption ====")
            generated_ids = self.model.generate(**inputs, max_new_tokens=256)
            
            # Extract only the generated part (not the input)
            generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
            
            # Decode the output tokens to text
            output_text = self._processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )
            
            # Get the final description
            description = (output_text[0].strip() if output_text else "No description generated")
            logger.info("==== Image description generated successfully ====")
            logger.info(description)
            
            return InferenceResponse(
                status=InferenceStatus.COMPLETED, 
                message="Image description generated successfully.", 
                data=description
            )
            
        except Exception as e:
            # Handle any errors during inference
            logger.error(f"==== Error: {str(e)} ====")
            return InferenceResponse(
                status=InferenceStatus.FAILED, 
                message=f"Error: {str(e)}"
            )

