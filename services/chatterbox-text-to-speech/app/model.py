import logging
import time
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
import io
import requests
import tempfile
import os
from typing import Dict, Any
from .config import settings
from .common import InferenceModel, ModelState

logger = logging.getLogger(__name__)

class ChatterboxModel(InferenceModel):
    """Chatterbox TTS model."""

    def __init__(self):
        super().__init__()

    def load_model(self):
        self.loading_start_time = time.time()
        try:
            # Load model
            model_kwargs = {
                "device": "cuda",
                "trust_remote_code": True,
            }
            
            if settings.HUGGINGFACE_CACHE_DIR:
                model_kwargs["cache_dir"] = settings.HUGGINGFACE_CACHE_DIR

            try:
                self.model = ChatterboxTTS.from_pretrained(
                    device="cuda"
                )
            except Exception as cuda_error:
                # Based on memory from previous issues with ChatterboxTTS and CUDA
                logger.warning(f"Failed to load model with CUDA: {str(cuda_error)}. Falling back to CPU.")
                raise

            # Successfully loaded
            self.state = ModelState.IDLE
            total_time = time.time() - self.loading_start_time
            logger.info(f"======== Model loaded successfully and ready for inference - Total loading time: {total_time:.2f} seconds ({total_time/60:.2f} minutes) ========")
            
            return self.model
        except Exception as e:
            logger.error(f"Chatterbox TTS model loading failed: {str(e)}")
            self.state = ModelState.ERROR
            self.error_message = str(e)
            raise

    def is_loaded(self):
        """Check if model is loaded."""
        return self.model is not None
    
    def inference(self, request_data: Dict[str, Any]) -> bytes:
        try:
            text = request_data.get('text', '')
            logger.info(f"\n\n\n# Processing text: {text}")

            voice_url = request_data.get('voice_url', None)
            logger.info(f"ChatterboxModel: generating audio from {text} with voice_url: {voice_url}")

            if not text:
                raise ValueError("Text is required")
            
            if not self.is_loaded():
                logger.warning("Model not loaded, attempting to load now")
                self.load_model()
            
            audio_prompt_path = None
            temp_file = None
            
            # If voice URL is provided, download it to a temporary file
            if voice_url:
                try:
                    response = requests.get(voice_url)
                    response.raise_for_status()
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                    temp_file.write(response.content)
                    temp_file.close()
                    audio_prompt_path = temp_file.name
                    logger.info(f"Downloaded voice from URL: {voice_url}")
                except Exception as e:
                    logger.error(f"Error downloading voice: {str(e)}")
                    audio_prompt_path = None

            
            if audio_prompt_path:
                wav = self.model.generate(text, exaggeration=0.7, cfg_weight=0.4, audio_prompt_path=audio_prompt_path)
            else:
                wav = self.model.generate(text, exaggeration=0.7, cfg_weight=0.4)
            
            # Clean up temporary file
            if temp_file and audio_prompt_path:
                try:
                    os.unlink(audio_prompt_path)
                    logger.info("Cleaned up temporary voice file")
                except Exception as e:
                    logger.warning(f"Could not clean up temp file: {str(e)}")
            
            # Save to memory buffer instead of file
            buffer = io.BytesIO()
            ta.save(buffer, wav, self.model.sr, format="wav")
            audio_bytes = buffer.getvalue()
            buffer.close()

            
            logger.info("ChatterboxModel: audio generated successfully")
            return audio_bytes

        except Exception as e:
            logger.error(f"ChatterboxModel error: {str(e)}")
            raise
