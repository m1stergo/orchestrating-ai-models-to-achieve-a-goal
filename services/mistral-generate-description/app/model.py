import logging
import asyncio
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Mistral model will be disabled.")


class MistralModel:
    """Local Mistral model for text generation (aligned with other providers)."""

    def __init__(self):
        from config import settings
        # Puedes usar: "mistralai/Mistral-7B-Instruct-v0.3" o el que prefieras
        self.model_name = getattr(settings, "MISTRAL_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        self.has_gpu = TRANSFORMERS_AVAILABLE and torch.cuda.is_available()
        self.device = "cuda" if self.has_gpu else "cpu"

    def is_available(self) -> bool:
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers library not available for Mistral model")
            return False
        return True

    async def generate_description(self, text: str, prompt: str) -> str:
        """Generate description using local Mistral model."""
        if not self.is_available():
            raise Exception("Transformers library not available")

        await self.is_loaded()

        # Construimos el prompt final con chat template si existe
        input_text = self._build_chat_prompt(text, prompt)

        try:
            # Ejecutar la generación pesada en un thread
            generated = await asyncio.to_thread(self._generate_sync, input_text)
            logger.info("Mistral model generated description successfully")
            return generated.strip()
        except Exception as e:
            logger.error(f"Error in Mistral generation: {str(e)}")
            raise Exception(f"Mistral model failed: {str(e)}")

    async def is_loaded(self):
        if self.model is not None and self.tokenizer is not None:
            return

        if not TRANSFORMERS_AVAILABLE:
            raise Exception("Transformers library not available")

        logger.info(f"Loading Mistral model: {self.model_name}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )

            # dtype y device_map automáticos cuando hay GPU
            dtype = "auto" if self.has_gpu else torch.float32
            device_map = "auto" if self.has_gpu else None
            max_memory = {0: "14GB", "cpu": "8GB"} if self.has_gpu else None

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=dtype,
                device_map=device_map,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                max_memory=max_memory
            )

            if not self.has_gpu:
                self.model = self.model.to(self.device)

            logger.info("Mistral model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Mistral model: {str(e)}")
            raise Exception(f"Model loading failed: {str(e)}")

    def _build_chat_prompt(self, text: str, prompt: str) -> str:
        """Usa chat template si está disponible, de lo contrario usa [INST]."""
        # Estructura de mensajes estilo chat
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{prompt}\n\nText to process:\n{text}"}
        ]

        if hasattr(self.tokenizer, "apply_chat_template"):
            try:
                return self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            except Exception:
                pass  # fallback a plantilla manual

        # Fallback compatible con modelos Instruct
        return f"<s>[INST] {prompt}\n\nText to process:\n{text} [/INST]"

    def _generate_sync(self, input_text: str) -> str:
        """Generación síncrona ejecutada en un thread."""
        # Tokenización
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

        # Generación
        with torch.inference_mode():
            outputs = self.model.generate(**inputs, **gen_kwargs)

        # Corta el prompt y decodifica solo lo nuevo
        prompt_len = inputs["input_ids"].shape[1]
        generated_tokens = outputs[0][prompt_len:]
        text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        return text
