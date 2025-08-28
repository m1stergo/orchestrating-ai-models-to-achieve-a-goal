from PIL import Image
from io import BytesIO
import requests
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
from qwen_vl_utils import process_vision_info
import torch
from .schemas import DescribeImageResponse
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class QwenModel:
    """ModelImageDescriptionModel for image description using Qwen2.5-VL model (local)."""

    def __init__(self, max_width: int = 512):
        self._model = None
        self._processor = None
        self.max_width = max_width

    async def is_loaded(self):
        """Ensures that the model is loaded asynchronously."""
        if self._model is None or self._processor is None:
            start_time = time.time()
            logger.info("Loading Qwen2.5-VL model... This may take several minutes.")
            model_name = "Qwen/Qwen2.5-VL-7B-Instruct"

            # Execute model loading in a separate thread to avoid blocking
            import asyncio
            logger.info("Starting model download and initialization...")
            await asyncio.to_thread(self._load_model_sync, model_name)
            
            total_time = time.time() - start_time
            logger.info(f"Qwen2.5-VL model loaded successfully and ready for inference - Total loading time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")

        return self._model, self._processor
        
    def _load_model_sync(self, model_name):
        """Loads the model synchronously (to be executed in a separate thread)."""
        model_start = time.time()
        logger.info(f"Downloading model {model_name}...")
        
        self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,          # if your GPU doesn't support bfloat16, you can use "auto"
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            max_memory={0: "14GB", "cpu": "8GB"}
        )
        model_time = time.time() - model_start
        logger.info(f"Model downloaded and loaded in {model_time:.2f} seconds ({model_time/60:.2f} minutes)")
        
        processor_start = time.time()
        logger.info("Loading processor...")
        self._processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        processor_time = time.time() - processor_start
        logger.info(f"Processor loaded in {processor_time:.2f} seconds")
        logger.info("Model initialization complete")

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
        logger.info(f"QwenModel: describing image from {image_url}")
        try:
            model, processor = await self.is_loaded()

            image = self._download_and_resize_image(image_url)

            if prompt is None:
                PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "default.txt"
                prompt = PROMPT_PATH.read_text(encoding="utf-8")

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

            logger.info("Generating caption with Qwen2.5-VL...")
            generated_ids = model.generate(**inputs, max_new_tokens=256)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )

            description = output_text[0].strip() if output_text else "No description generated"
            logger.info("QwenModel: description generated successfully")
            return description

        except Exception as e:
            logger.error(f"QwenModel error: {str(e)}")
            raise
