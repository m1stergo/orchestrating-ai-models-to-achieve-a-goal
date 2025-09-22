"""Mistral text generation model handler implementation.

This module provides the MistralHandler class that implements the InferenceHandler
interface for the Mistral large language model. It handles model loading, text processing,
and running inference to generate product descriptions based on image descriptions.

The handler supports downloading the model from HuggingFace, proper prompt formatting,
and generating structured text outputs for product information.
"""

import logging
import time
from typing import Any, Optional, Dict
from .config import settings
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from .common import InferenceHandler, InferenceResponse, InferenceStatus
import os
from huggingface_hub import snapshot_download

# Configure module logger
logger = logging.getLogger(__name__)

class MistralHandler(InferenceHandler):
    """Handler for Mistral language model inference.
    
    This class implements the InferenceHandler interface for the Mistral
    large language model. It handles model loading, text processing,
    and running inference to generate product descriptions based on
    image descriptions.
    
    Attributes:
        model_name: Name or path of the Mistral model to use
        tokenizer: Text tokenizer for encoding and decoding
    """
    def __init__(self, model_name: str):
        """Initialize the Mistral handler.
        
        Args:
            model_name: Name or path of the Mistral model to use
        """
        super().__init__(model_name)
        self.tokenizer: Optional[Any] = None

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
        """Load the Mistral language model into memory.
        
        This method implements the abstract method from InferenceHandler.
        It downloads the model if needed, then loads both the tokenizer and model
        with optimal settings for memory management and GPU utilization.
        
        Returns:
            InferenceResponse: Response with status of the model loading operation
            
        Note:
            This is a resource-intensive operation that may take several minutes
            depending on the model size and hardware configuration.
        """
        try:
            logger.info("==== Loading model... This may take several minutes. ====")

            local_repo = self._materialize_model()

            # Load tokenizer
            tokenizer_kwargs = {
                "trust_remote_code": True,
                "offload_folder": "/runpod-volume/offload",
                "token": settings.HF_TOKEN
            }
                
            self.tokenizer = AutoTokenizer.from_pretrained(
                local_repo,
                **tokenizer_kwargs
            )

            # Load model
            model_kwargs = {
                "torch_dtype": "auto",
                "device_map": "auto",
                "trust_remote_code": True,
                "offload_folder": "/runpod-volume/offload",
                "token": settings.HF_TOKEN
            }
            
            if settings.HUGGINGFACE_CACHE_DIR:
                model_kwargs["cache_dir"] = settings.HUGGINGFACE_CACHE_DIR

            self.model = AutoModelForCausalLM.from_pretrained(
                local_repo,
                **model_kwargs
            )

            # Successfully loaded
            self.status = InferenceStatus.COMPLETED
            total_time = time.time() - self.loading_start_time
            logger.info(f"==== Model loaded successfully and ready for inference - Total loading time: {total_time:.2f} seconds ({total_time/60:.2f} minutes) ====")
            
            return InferenceResponse(
                status=InferenceStatus.COMPLETED,
                message="Model is ready to use.",
                data=""
            )
            
        except Exception as e:
            logger.error(f"==== Failed to load Mistral model: {str(e)} ====")
            self.status = InferenceStatus.FAILED
            self.error_message = str(e)
            return InferenceResponse(
                status=InferenceStatus.FAILED,
                message=f"Failed to load model: {str(e)}",
                data=""
            )
            
    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready for inference.
        
        This method implements the abstract method from InferenceHandler.
        It verifies that both the model and tokenizer are loaded.
        
        Returns:
            bool: True if the model and tokenizer are loaded, False otherwise
        """
        return self.model is not None and self.tokenizer is not None

    def infer(self, request_data: Dict[str, Any]) -> InferenceResponse:
        """Run inference to generate a product description.
        
        This method implements the abstract method from InferenceHandler.
        It processes input text describing a product image and generates a structured
        product description including title, description, keywords, and category.
        
        Args:
            request_data: Dictionary with inference parameters including:
                - text: Description of the product image (required)
                - prompt: Custom prompt to use (optional)
                
        Returns:
            InferenceResponse: Response with the generated product description
            
        Note:
            If the model is not loaded, this will trigger model loading
            and return a warming up status.
        """
        logger.info(f"==== Generating product description ====")

        try:
            if not self.is_loaded():
                self.load_model()
            
            # Set state to IN_PROGRESS before starting generation
            self.status = InferenceStatus.IN_PROGRESS
            
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

            # Reset state to COMPLETED after processing
            self.status = InferenceStatus.COMPLETED
            
            logger.info("==== Product description generated successfully ====")
            logger.info(f"==== {text} ====")
            return InferenceResponse(
                status=InferenceStatus.COMPLETED,
                message="Product description generated successfully.",
                data=text.strip()
            )
        except Exception as e:
            logger.error(f"==== Error: {str(e)} ====")
            return InferenceResponse(
                status=InferenceStatus.FAILED,
                message=f"Error: {str(e)}",
                data=""
            )

    def _build_chat_prompt(self, text: str, prompt: str) -> str:
        """Build a properly formatted chat prompt for the model.
        
        This method formats the input text and prompt into the proper chat format
        expected by the Mistral model, using the model's chat template if available.
        
        Args:
            text: The input text (image description) to process
            prompt: The system prompt with instructions
            
        Returns:
            str: Formatted chat prompt ready for the model
            
        Note:
            Falls back to a simpler format if chat template is not available.
        """
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]

        try:
            logger.info("==== Using apply_chat_template ====")
            return self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        except Exception:
            logger.info("==== Using fallback prompt ====")
            pass

    def _generate_sync(self, input_text: str) -> str:
        """Generate text synchronously using the Mistral model.
        
        This is a helper method that handles the actual text generation process
        using the model and tokenizer. It configures generation parameters for
        optimal output quality.
        
        Args:
            input_text: The prepared input text to send to the model
            
        Returns:
            str: Generated text from the model
        """
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
