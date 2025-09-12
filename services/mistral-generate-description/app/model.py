import logging
import time
from typing import Any, Optional, Dict
from .config import settings
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from .common import InferenceModel, ModelState

logger = logging.getLogger(__name__)

class MistralModel(InferenceModel):
    """Local Mistral model for text generation (aligned with other providers)."""
    def __init__(self):
        super().__init__()
        self.tokenizer: Optional[Any] = None
        
    @property
    def device(self):
        """Get the device to use for model inference."""
        return torch.device('cuda') if self.has_gpu else torch.device('cpu')
    
    def load_model(self):
        """Ensures that the model is loaded synchronously."""
        super().load_model()

        try:
            # Load tokenizer
            tokenizer_kwargs = {
                "trust_remote_code": True, 
                "token": settings.HF_TOKEN
            }
            if settings.HUGGINGFACE_CACHE_DIR:
                tokenizer_kwargs["cache_dir"] = settings.HUGGINGFACE_CACHE_DIR
                
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                **tokenizer_kwargs
            )

            # Load model
            model_kwargs = {
                "torch_dtype": "auto",
                "device_map": "auto",
                "trust_remote_code": True,
                "token": settings.HF_TOKEN
            }
            
            if settings.HUGGINGFACE_CACHE_DIR:
                model_kwargs["cache_dir"] = settings.HUGGINGFACE_CACHE_DIR

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )

            # Successfully loaded
            self.state = ModelState.IDLE
            total_time = time.time() - self.loading_start_time
            logger.info(f"======== Model loaded successfully and ready for inference - Total loading time: {total_time:.2f} seconds ({total_time/60:.2f} minutes) ========")
            
            return self.model, self.tokenizer
            
        except Exception as e:
            logger.error(f"======== Failed to load Mistral model: {str(e)} ========")
            self.state = ModelState.ERROR
            self.error_message = str(e)
            raise Exception(f"Model loading failed: {str(e)}")
            
    def is_loaded(self):
        """Check if model is loaded."""
        return self.model is not None and self.tokenizer is not None

    def inference(self, request_data: Dict[str, Any]) -> str:
        logger.info(f"======== Processing text content ========")

        try:
            if not self.is_loaded():
                self.load_model()
            
            # Set state to PROCESSING before starting generation
            self.state = ModelState.PROCESSING
            
            # Extract text and prompt from request_data
            text = request_data.get('text', '')
            prompt = request_data.get('prompt', settings.PROMPT)

            
            input_text = self._build_chat_prompt(text, prompt)

            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            )

            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

            gen_kwargs = dict(
                max_new_tokens=500,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
                use_cache=True,
            )

            with torch.inference_mode():
                outputs = self.model.generate(**inputs, **gen_kwargs)

            prompt_len = inputs["input_ids"].shape[1]
            generated_tokens = outputs[0][prompt_len:]
            text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

            # Reset state to IDLE after processing
            self.state = ModelState.IDLE
            
            logger.info("======== Description generated successfully ========")
            logger.info(f"======== {text} ========")
            return text.strip()
        except Exception as e:
            logger.error(f"======== Error: {str(e)} ========")
            raise

    def _build_chat_prompt(self, text: str, prompt: str) -> str:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]

        try:
            logger.info("======== Using apply_chat_template ========")
            return self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        except Exception:
            logger.info("======== Using fallback prompt ========")
            pass

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
