from PIL import Image
from io import BytesIO
import requests
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
from qwen_vl_utils import process_vision_info
import torch
import logging
import time
from app.config import settings

logger = logging.getLogger(__name__)

class QwenModel:
    """ImageDescriptionModel for image description using model (local)."""

    def __init__(self, max_width: int = 512):
        self._model = None
        self._processor = None
        self.max_width = max_width

    async def is_loaded(self):
        """Ensures that the model is loaded asynchronously."""
        if self._model is None or self._processor is None:
            start_time = time.time()
            logger.info("Loading model... This may take several minutes.")
            model_name = settings.QWEN_MODEL_NAME

            # Execute model loading in a separate thread to avoid blocking
            import asyncio
            logger.info("Starting model download and initialization...")
            await asyncio.to_thread(self._load_model_sync, model_name)
            
            total_time = time.time() - start_time
            logger.info(f"Model loaded successfully and ready for inference - Total loading time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")

        return self._model, self._processor
        
    def _load_model_sync(self, model_name):
        """Loads the model synchronously (to be executed in a separate thread)."""
        import os
        import shutil
        import glob
        import stat
        import fcntl
        from pathlib import Path
        
        model_start = time.time()
        logger.info(f"Downloading model {model_name}...")
        
        # Set up Hugging Face authentication if token is provided
        if settings.HF_TOKEN:
            os.environ['HF_TOKEN'] = settings.HF_TOKEN
            logger.info("Using HF authentication token")
        
        # Ensure cache directory exists and has proper permissions
        cache_dir = os.environ.get('HF_HUB_CACHE', '/app/models')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Clean up any existing lock files and incomplete downloads
        self._cleanup_cache_locks(cache_dir, model_name)
        
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Model loading attempt {attempt + 1}/{max_retries}")
                
                self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                    model_name,
                    torch_dtype=torch.bfloat16,
                    device_map="auto",
                    trust_remote_code=True,
                    low_cpu_mem_usage=True,
                    max_memory={0: settings.QWEN_MAX_MEMORY_GPU, "cpu": settings.QWEN_MAX_MEMORY_CPU},
                    force_download=False,  # Use cache if available
                    resume_download=True   # Resume interrupted downloads
                )
                break  # Success, exit retry loop
                
            except (PermissionError, OSError) as e:
                logger.error(f"Error loading model (attempt {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    # Clean up and retry
                    self._cleanup_cache_locks(cache_dir, model_name)
                    logger.info(f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                else:
                    # Last attempt failed, try force download
                    logger.warning("All retries failed, attempting force download...")
                    self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                        model_name,
                        torch_dtype=torch.bfloat16,
                        device_map="auto",
                        trust_remote_code=True,
                        low_cpu_mem_usage=True,
                        max_memory={0: settings.QWEN_MAX_MEMORY_GPU, "cpu": settings.QWEN_MAX_MEMORY_CPU},
                        force_download=True  # Force fresh download
                    )
        
        model_time = time.time() - model_start
        logger.info(f"Model downloaded and loaded in {model_time:.2f} seconds ({model_time/60:.2f} minutes)")
        
        processor_start = time.time()
        logger.info("Loading processor...")
        
        # Apply same retry logic for processor
        for attempt in range(max_retries):
            try:
                self._processor = AutoProcessor.from_pretrained(
                    model_name, 
                    trust_remote_code=True,
                    force_download=False,
                    resume_download=True
                )
                break
            except (PermissionError, OSError) as e:
                logger.error(f"Error loading processor (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    self._processor = AutoProcessor.from_pretrained(
                        model_name, 
                        trust_remote_code=True,
                        force_download=True
                    )
            
        processor_time = time.time() - processor_start
        logger.info(f"Processor loaded in {processor_time:.2f} seconds")
        logger.info("Model initialization complete")
    
    def _cleanup_cache_locks(self, cache_dir, model_name):
        """Clean up Hugging Face cache lock files and incomplete downloads."""
        import os
        import glob
        import shutil
        from pathlib import Path
        
        model_cache_name = model_name.replace('/', '--')
        model_cache_path = os.path.join(cache_dir, f"models--{model_cache_name}")
        
        try:
            # Remove .lock files
            lock_files = glob.glob(os.path.join(cache_dir, "**/*.lock"), recursive=True)
            for lock_file in lock_files:
                try:
                    os.remove(lock_file)
                    logger.info(f"Removed lock file: {lock_file}")
                except Exception as e:
                    logger.warning(f"Could not remove lock file {lock_file}: {e}")
            
            # Remove .tmp directories and files
            tmp_patterns = [
                os.path.join(cache_dir, "**/.tmp*"),
                os.path.join(cache_dir, "**/tmp*"),
                os.path.join(model_cache_path, "**/.tmp*") if os.path.exists(model_cache_path) else None
            ]
            
            for pattern in tmp_patterns:
                if pattern:
                    tmp_items = glob.glob(pattern, recursive=True)
                    for tmp_item in tmp_items:
                        try:
                            if os.path.isdir(tmp_item):
                                shutil.rmtree(tmp_item)
                            else:
                                os.remove(tmp_item)
                            logger.info(f"Removed temporary item: {tmp_item}")
                        except Exception as e:
                            logger.warning(f"Could not remove temporary item {tmp_item}: {e}")
            
            # Fix permissions on cache directory
            if os.path.exists(model_cache_path):
                try:
                    # Recursively fix permissions
                    for root, dirs, files in os.walk(model_cache_path):
                        for d in dirs:
                            os.chmod(os.path.join(root, d), 0o755)
                        for f in files:
                            os.chmod(os.path.join(root, f), 0o644)
                    logger.info(f"Fixed permissions for {model_cache_path}")
                except Exception as e:
                    logger.warning(f"Could not fix permissions: {e}")
                    
        except Exception as e:
            logger.warning(f"Cache cleanup failed: {e}")

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

    async def describe_image(self, image_url: str, prompt: str = None) -> str:
        logger.info(f"describing image from {image_url}")
        try:
            model, processor = await self.is_loaded()

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

            text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            image_inputs, video_inputs = process_vision_info(messages)

            inputs = processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            ).to(model.device)

            logger.info("Generating caption")
            generated_ids = model.generate(**inputs, max_new_tokens=256)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )

            description = output_text[0].strip() if output_text else "No description generated"
            logger.info("description generated successfully")
            return description

        except Exception as e:
            logger.error(f"error: {str(e)}")
            raise
