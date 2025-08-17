import logging
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
import io
import requests
import tempfile
import os
logger = logging.getLogger(__name__)

class ChatterboxModel:
    """Chatterbox TTS model."""

    def __init__(self):
        self._model = None

    def is_loaded(self):
        """Ensures that the model is loaded."""
        if self._model is None:
            logger.info("Loading Chatterbox TTS model...")
            
            # Debug info
            import torch
            logger.info(f"PyTorch version: {torch.__version__}")
            logger.info(f"CUDA available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                logger.info(f"CUDA device count: {torch.cuda.device_count()}")
                logger.info(f"Current CUDA device: {torch.cuda.current_device()}")
            
            # Try CUDA first, fallback to CPU if ChatterboxTTS has issues
            try:
                if torch.cuda.is_available():
                    logger.info("Attempting to load ChatterboxTTS with CUDA...")
                    self._model = ChatterboxTTS.from_pretrained(device="cuda")
                    logger.info("Successfully loaded ChatterboxTTS with CUDA")
                else:
                    raise Exception("PyTorch CUDA not available")
            except Exception as e:
                logger.warning(f"ChatterboxTTS CUDA failed: {str(e)}, falling back to CPU")
                try:
                    self._model = ChatterboxTTS.from_pretrained(device="cpu")
                    logger.info("Successfully loaded ChatterboxTTS with CPU")
                except Exception as cpu_e:
                    logger.error(f"ChatterboxTTS CPU also failed: {str(cpu_e)}")
                    raise
            logger.info("Chatterbox TTS model loaded successfully")

        return self._model

    def generate_audio(self, text: str, audio_prompt_url: str = None) -> bytes:
        logger.info(f"ChatterboxModel: generating audio from {text}")
        try:
            model = self.is_loaded()
            
            audio_prompt_path = None
            temp_file = None
            
            # If audio prompt URL is provided, download it to a temporary file
            if audio_prompt_url:
                try:
                    response = requests.get(audio_prompt_url)
                    response.raise_for_status()
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                    temp_file.write(response.content)
                    temp_file.close()
                    audio_prompt_path = temp_file.name
                    logger.info(f"Downloaded audio prompt from URL: {audio_prompt_url}")
                except Exception as e:
                    logger.error(f"Error downloading audio prompt: {str(e)}")
                    audio_prompt_path = None

            
            if audio_prompt_path:
                wav = model.generate(text, exaggeration=0.7, cfg_weight=0.4, audio_prompt_path=audio_prompt_path)
            else:
                wav = model.generate(text, exaggeration=0.7, cfg_weight=0.4)
            
            # Clean up temporary file
            if temp_file and audio_prompt_path:
                try:
                    os.unlink(audio_prompt_path)
                    logger.info("Cleaned up temporary audio prompt file")
                except Exception as e:
                    logger.warning(f"Could not clean up temp file: {str(e)}")
            
            # Save to memory buffer instead of file
            buffer = io.BytesIO()
            ta.save(buffer, wav, model.sr, format="wav")
            audio_bytes = buffer.getvalue()
            buffer.close()

            
            logger.info("ChatterboxModel: audio generated successfully")
            return audio_bytes

        except Exception as e:
            logger.error(f"ChatterboxModel error: {str(e)}")
            raise
