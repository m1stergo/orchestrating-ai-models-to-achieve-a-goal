import logging
from typing import Dict, Any, Optional
from .base import BaseGenerateDescriptionStrategy

logger = logging.getLogger(__name__)

# Import transformers components conditionally
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Mistral strategy will be disabled.")


class MistralStrategy(BaseGenerateDescriptionStrategy):
    """Local Mistral strategy for text generation."""
    
    def __init__(self):
        super().__init__()
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.1"
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    async def _load_model(self):
        """Load the Mistral model and tokenizer."""
        if not TRANSFORMERS_AVAILABLE:
            raise Exception("Transformers library not available")
            
        if self.model is None or self.tokenizer is None:
            logger.info(f"Loading Mistral model: {self.model_name}")
            
            try:
                # Load tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    trust_remote_code=True
                )
                
                # Load model with memory optimization
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True,
                    max_memory={0: "14GB", "cpu": "8GB"} if self.device == "cuda" else None
                )
                
                if self.device == "cpu":
                    self.model = self.model.to(self.device)
                    
                logger.info("Mistral model loaded successfully")
                
            except Exception as e:
                logger.error(f"Failed to load Mistral model: {str(e)}")
                raise Exception(f"Model loading failed: {str(e)}")
    
    def _build_prompt(self, text: str, prompt: str) -> str:
        """Build the formatted prompt for Mistral."""
        return f"<s>[INST] {prompt}\n\nText to process:\n{text} [/INST]"
    
    async def generate_description(self, text: str, prompt: str) -> str:
        """Generate description using local Mistral model."""
        if not TRANSFORMERS_AVAILABLE:
            raise Exception("Transformers library not available")
            
        await self._load_model()
        
        try:
            # Build the prompt
            full_prompt = self._build_prompt(text, prompt)
            
            # Tokenize input
            inputs = self.tokenizer(
                full_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=500,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    top_k=50,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode the response
            generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
            generated_text = self.tokenizer.decode(
                generated_tokens,
                skip_special_tokens=True
            ).strip()
            
            logger.info("Mistral strategy generated description successfully")
            return generated_text
            
        except Exception as e:
            logger.error(f"Error in Mistral generation: {str(e)}")
            raise Exception(f"Mistral strategy failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Mistral dependencies are available."""
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers library not available for Mistral strategy")
            return False
        return True
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get Mistral strategy information."""
        return {
            "name": self.name,
            "model": self.model_name,
            "type": "local",
            "provider": "Mistral AI",
            "description": "Local Mistral-7B text generation",
            "requires_api_key": False,
            "device": self.device,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "cuda_available": torch.cuda.is_available() if TRANSFORMERS_AVAILABLE else False
        }
