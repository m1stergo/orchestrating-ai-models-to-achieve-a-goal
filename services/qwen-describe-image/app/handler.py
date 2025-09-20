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

logger = logging.getLogger(__name__)

class QwenHandler(InferenceHandler):
    def __init__(self, model_name: str, max_width: int = 512):
        super().__init__(model_name)
        self._processor = None
        self.max_width = max_width

    def _materialize_model(self) -> str:
        # Usar la configuración centralizada de Pydantic
        base_models_dir = settings.MODELS_DIR
        local_dir = f"{base_models_dir}/{self.model_name.replace('/', '__')}"
        os.makedirs(local_dir, exist_ok=True)
        cache_dir = settings.HUGGINGFACE_CACHE_DIR
        logger.info(f"==== snapshot_download to {local_dir} (cache: {cache_dir}) ====")
        path = snapshot_download(
            repo_id=self.model_name,
            cache_dir=cache_dir,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
            allow_patterns=["*.safetensors","*.bin","*.json","tokenizer.*","processor.*","*.model","vocab.*","merges.txt",".gitattributes"],
            ignore_patterns=["images/*","assets/*","examples/*","docs/*","test*/*","*.md"],
        )
        return path

    def _do_load_model(self) -> InferenceResponse:
        try:
            logger.info("==== Loading model... This may take several minutes. ====")

            local_repo = self._materialize_model()

            model_kwargs = {
                "trust_remote_code": True,
                "device_map": "auto",
                "low_cpu_mem_usage": True,
                "offload_folder": "/runpod-volume/offload",
                "torch_dtype": "auto",
                "max_memory": {0: settings.QWEN_MAX_MEMORY_GPU, "cpu": settings.QWEN_MAX_MEMORY_CPU},
            }

            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(local_repo, **model_kwargs)
            self._processor = AutoProcessor.from_pretrained(local_repo, trust_remote_code=True)

            self.status = InferenceStatus.COMPLETED
            total_time = time.time() - self.loading_start_time
            logger.info(f"==== Model loaded successfully and ready for inference - {total_time:.2f}s ({total_time/60:.2f}m) ====")
            return InferenceResponse(status=InferenceStatus.COMPLETED, message="Model is ready to use.")

        except Exception as e:
            logger.error(f"==== Failed to load model: {e} ====")
            self.status = InferenceStatus.FAILED
            self.error_message = str(e)
            return InferenceResponse(status=InferenceStatus.FAILED, message=f"Failed to load model: {e}")

    def is_loaded(self):
        return self.model is not None and self._processor is not None

    def _download_and_resize_image(self, image_url: str) -> Image.Image:
        resp = requests.get(image_url)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert("RGB")
        if img.width > self.max_width:
            ratio = self.max_width / float(img.width)
            img = img.resize((self.max_width, int(img.height * ratio)), Image.LANCZOS)
        return img

    def infer(self, request_data: Dict[str, Any]) -> InferenceResponse:
        try:
            image_url = request_data.get('image_url')
            if not image_url:
                raise ValueError("The 'image_url' parameter is required for this model")
            logger.info(f"==== Describing image from {image_url} ====")

            if not self.is_loaded():
                self.load_model()
                return InferenceResponse(status=InferenceStatus.WARMINGUP, message="Model is warming up...")

            image = self._download_and_resize_image(image_url)
            prompt = request_data.get('prompt', settings.PROMPT)
            messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": prompt}]}]

            text = self._processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self._processor(text=[text], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt").to(self.model.device)

            logger.info("==== Generating caption ====")
            generated_ids = self.model.generate(**inputs, max_new_tokens=256)
            generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
            output_text = self._processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)
            description = (output_text[0].strip() if output_text else "No description generated")
            logger.info("==== Image description generated successfully ====")
            logger.info(description)
            return InferenceResponse(status=InferenceStatus.COMPLETED, message="Image description generated successfully.", data=description)
        except Exception as e:
            logger.error(f"==== Error: {str(e)} ====")
            return InferenceResponse(status=InferenceStatus.FAILED, message=f"Error: {str(e)}")

