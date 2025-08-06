from PIL import Image
from io import BytesIO
import requests
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
from qwen_vl_utils import process_vision_info
import torch
from schemas import DescribeImageResponse
from .base import ImageDescriptionModel
import logging

logger = logging.getLogger(__name__)

class QwenModel(ImageDescriptionModel):
    """ModelImageDescriptionModel for image description using Qwen2.5-VL model (local)."""

    def __init__(self, max_width: int = 512):
        super().__init__()
        self._model = None
        self._processor = None
        self.max_width = max_width

    def is_available(self) -> bool:
        try:
            from transformers import Qwen2_5_VLForConditionalGeneration  # noqa: F401
            from qwen_vl_utils import process_vision_info  # noqa: F401
            return True
        except ImportError:
            return False

    def _load_qwen_model(self):
        if self._model is None or self._processor is None:
            logger.info("Loading Qwen2.5-VL model...")
            model_name = "Qwen/Qwen2.5-VL-7B-Instruct"

            self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.bfloat16,          # si tu GPU no soporta bfloat16, podés usar "auto"
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                max_memory={0: "14GB", "cpu": "8GB"}
            )
            self._processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
            logger.info("Qwen2.5-VL model loaded successfully")

        return self._model, self._processor

    def _download_and_resize_image(self, image_url: str) -> Image.Image:
        """Descarga la imagen y la redimensiona a max_width si hace falta."""
        resp = requests.get(image_url)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert("RGB")

        if img.width > self.max_width:
            ratio = self.max_width / float(img.width)
            new_h = int(img.height * ratio)
            img = img.resize((self.max_width, new_h), Image.LANCZOS)

        return img

    async def describe_image(self, image_url: str, prompt: str = None) -> DescribeImageResponse:
        logger.info(f"QwenModel: describing image from {image_url}")
        try:
            model, processor = self._load_qwen_model()

            image = self._download_and_resize_image(image_url)

            if prompt is None:
                from pathlib import Path
                PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "default.txt"
                prompt = PROMPT_PATH.read_text(encoding="utf-8")

            # Usamos el PIL.Image ya redimensionado en el mensaje
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
            return DescribeImageResponse(description=description)

        except Exception as e:
            logger.error(f"QwenModel error: {str(e)}")
            raise
