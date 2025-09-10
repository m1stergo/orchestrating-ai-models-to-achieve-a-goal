import logging
import time
import os
from enum import Enum
from typing import Any, Optional
from .config import settings
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

logger = logging.getLogger(__name__)

class ModelState(Enum):
    COLD = "COLD"
    WARMINGUP = "WARMINGUP"
    PROCESSING = "PROCESSING"
    IDLE = "IDLE"
    ERROR = "ERROR"

class MistralModel:
    """Local Mistral model for text generation (aligned with other providers)."""
    def __init__(self):
        self.model_name = None
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        self._state = ModelState.COLD
        self._loading_start_time = None
        self._error_message = None
        
    @property
    def has_gpu(self) -> bool:
        """Check if GPU is available for model inference."""
        return torch.cuda.is_available()
        
    @property
    def device(self):
        """Get the device to use for model inference."""
        return torch.device('cuda') if self.has_gpu else torch.device('cpu')
    
    def load_model(self):
        """Ensures that the model is loaded synchronously."""
        if self.is_loaded():
            self._state = ModelState.IDLE
            return
            
        self._state = ModelState.WARMINGUP
        self._loading_start_time = time.time()
        self._error_message = None

        start_time = time.time()
        # Usar MISTRAL_MODEL_NAME en lugar de MISTRAL_MODEL_NAME_NAME
        self.model_name = settings.MISTRAL_MODEL_NAME
        logger.info(f"======== Loading Mistral model: {self.model_name}... This may take several minutes. ========")

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
            # Load tokenizer
            tokenizer_kwargs = {"trust_remote_code": True, "token": settings.HF_TOKEN}
            if hasattr(settings, 'HUGGINGFACE_CACHE_DIR') and settings.HUGGINGFACE_CACHE_DIR:
                tokenizer_kwargs["cache_dir"] = settings.HUGGINGFACE_CACHE_DIR
                
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                **tokenizer_kwargs
            )

            # Load model with appropriate settings based on hardware
            dtype = "auto" if self.has_gpu else torch.float32
            device_map = "auto" if self.has_gpu else None

            model_kwargs = {
                "torch_dtype": dtype,
                "device_map": device_map,
                "trust_remote_code": True,
                "token": settings.HF_TOKEN
            }
            
            if hasattr(settings, 'HUGGINGFACE_CACHE_DIR') and settings.HUGGINGFACE_CACHE_DIR:
                model_kwargs["cache_dir"] = settings.HUGGINGFACE_CACHE_DIR

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )

            if not self.has_gpu and device_map is None:
                self.model = self.model.to(self.device)

            # Successfully loaded model
            self._state = ModelState.IDLE
            total_time = time.time() - start_time
            logger.info(f"======== Model loaded successfully and ready for inference - Total loading time: {total_time:.2f} seconds ({total_time/60:.2f} minutes) ========")
            
            return self.model, self.tokenizer
            
        except Exception as e:
            logger.error(f"======== Failed to load Mistral model: {str(e)} ========")
            self._state = ModelState.ERROR
            self._error_message = str(e)
            raise Exception(f"Model loading failed: {str(e)}")
            
    def is_loaded(self):
        """Check if model is loaded."""
        return self.model is not None and self.tokenizer is not None

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

    async def inference(self, text: str, prompt: str) -> str:
        logger.info(f"======== Processing text content ========")

        try:
            if not self.is_loaded():
                self.load_model()
            
            # Set state to PROCESSING before starting generation
            self._state = ModelState.PROCESSING
            
            prompt = settings.PROMPT if prompt is None else prompt
            
            input_text = self._build_chat_prompt(text, prompt)

            logger.info("======== Generating description ========")
            generated = self._generate_sync(input_text)
            
            # Reset state to IDLE after processing
            self._state = ModelState.IDLE
            
            logger.info("======== Description generated successfully ========")
            logger.info(f"======== {generated} ========")
            return generated.strip()
        except Exception as e:
            logger.error(f"======== Error: {str(e)} ========")
            raise
            
    # Alias for backward compatibility
    async def generate_description(self, text: str, prompt: str) -> str:
        """Alias for inference method for backward compatibility."""
        return await self.inference(text, prompt)

    def _build_chat_prompt(self, text: str, prompt: str) -> str:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]

        if hasattr(self.tokenizer, "apply_chat_template"):
            try:
                return self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            except Exception:
                pass

        return f"<s>[INST] {prompt} {text} [/INST]"

    def _generate_sync(self, input_text: str) -> str:
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        )

        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        eos_id = self.tokenizer.eos_token_id
        pad_id = self.tokenizer.pad_token_id or eos_id

        gen_kwargs = dict(
            max_new_tokens=500,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            top_k=50,
            eos_token_id=eos_id,
            pad_token_id=pad_id,
            use_cache=True,
        )

        with torch.inference_mode():
            outputs = self.model.generate(**inputs, **gen_kwargs)

        prompt_len = inputs["input_ids"].shape[1]
        generated_tokens = outputs[0][prompt_len:]
        text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        return text
