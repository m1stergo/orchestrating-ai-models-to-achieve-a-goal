"""ChatterboxTTS model handler implementation.

This module provides the ChatterboxHandler class that implements the InferenceHandler
interface for the ChatterboxTTS text-to-speech model. It handles model loading, text processing,
and running inference to generate speech audio from text input.

The handler supports downloading the model from HuggingFace, voice cloning from audio samples,
and uploading generated audio to MinIO storage.
"""

import logging
import time
import os
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
import io
import requests
import tempfile
from typing import Dict, Any
from .config import settings
from .common import InferenceHandler, InferenceResponse, InferenceStatus
from uuid import uuid4
from huggingface_hub import snapshot_download
from app.minio_client import MinioClient

# Configure module logger
logger = logging.getLogger(__name__)

# Initialize MinIO client for storing generated audio
minio_client = MinioClient()

class ChatterboxHandler(InferenceHandler):
    """Handler for ChatterboxTTS model inference.
    
    This class implements the InferenceHandler interface for the ChatterboxTTS
    text-to-speech model. It handles model loading, text processing,
    audio generation, voice cloning, and storing the resulting audio files.
    
    Attributes:
        model_name: Name or path of the ChatterboxTTS model to use
        model: The loaded ChatterboxTTS model instance
    """

    def __init__(self, model_name: str):
        """Initialize the ChatterboxTTS handler.
        
        Args:
            model_name: Name or path of the ChatterboxTTS model to use
        """
        super().__init__(model_name)

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
        """Load the ChatterboxTTS model into memory.
        
        This method implements the abstract method from InferenceHandler.
        It downloads the model if needed, then loads it with CUDA support
        if available, falling back to CPU if needed.
        
        Returns:
            InferenceResponse: Response with status of the model loading operation
            
        Note:
            This is a resource-intensive operation that may take several minutes
            depending on the model size and hardware configuration.
        """
        self.loading_start_time = time.time()
        try:

            local_repo = self._materialize_model()

            # Load model
            model_kwargs = {
                "device": "cuda",
                "offload_folder": "/runpod-volume/offload",
                "trust_remote_code": True,
            }

            try:
                self.model = ChatterboxTTS.from_local(
                    ckpt_dir=local_repo,
                    device="cuda",
                )
            except Exception as cuda_error:
                # Based on memory from previous issues with ChatterboxTTS and CUDA
                logger.warning(f"Failed to load model with CUDA: {str(cuda_error)}. Falling back to CPU.")
                raise

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
            logger.error(f"Chatterbox TTS model loading failed: {str(e)}")
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
        It verifies that the model is loaded and ready for use.
        
        Returns:
            bool: True if the model is loaded, False otherwise
        """
        return self.model is not None
    
    def infer(self, request_data: Dict[str, Any]) -> InferenceResponse:
        """Run inference to generate speech audio from text.
        
        This method implements the abstract method from InferenceHandler.
        It processes input text and generates audio using the ChatterboxTTS model.
        It can optionally clone a voice from a provided audio sample URL.
        
        Args:
            request_data: Dictionary with inference parameters including:
                - text: Text to convert to speech (required)
                - voice_url: URL of an audio sample for voice cloning (optional)
                
        Returns:
            InferenceResponse: Response with URL to the generated audio
            
        Note:
            Generated audio is uploaded to MinIO storage and a URL is returned.
            If voice_url is provided, the model will attempt to clone that voice.
        """
        try:
            text = request_data.get('text', '')
            logger.info(f"==== Processing text: {text} ====")

            voice_url = request_data.get('voice_url', None)
            logger.info(f"==== ChatterboxModel: generating audio from {text} with voice_url: {voice_url} ====")

            if not text:
                raise ValueError("Text is required")
            
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
                    logger.info(f"==== Downloaded voice from URL: {voice_url} ====")
                except Exception as e:
                    logger.error(f"==== Error downloading voice: {str(e)} ====")
                    audio_prompt_path = None

            
            if audio_prompt_path:
                wav = self.model.generate(text, exaggeration=0.7, cfg_weight=0.4, audio_prompt_path=audio_prompt_path)
            else:
                wav = self.model.generate(text, exaggeration=0.7, cfg_weight=0.4)
            
            # Clean up temporary file
            if temp_file and audio_prompt_path:
                try:
                    os.unlink(audio_prompt_path)
                    logger.info("==== Cleaned up temporary voice file ====")
                except Exception as e:
                    logger.warning(f"==== Could not clean up temp file: {str(e)} ====")
            
            try:
                buffer = io.BytesIO()
                ta.save(buffer, wav, self.model.sr, format="wav")
                buffer.seek(0)
                
                # Subir el archivo usando el método upload_file del cliente
                audio_url = minio_client.upload_temp_file(
                    file_data=buffer,
                    content_type="audio/wav"
                )
                
                logger.info(f"==== Audio uploaded to MinIO: {audio_url} =====")
                
                return InferenceResponse(
                    status=InferenceStatus.COMPLETED,
                    message="Audio generated successfully.",
                    data=audio_url
                )
                
            except Exception as storage_error:
                logger.error(f"==== Error uploading to MinIO: {storage_error} ====")
                raise

        except Exception as e:
            logger.error(f"==== ChatterboxModel error: {str(e)} ====")
            raise
