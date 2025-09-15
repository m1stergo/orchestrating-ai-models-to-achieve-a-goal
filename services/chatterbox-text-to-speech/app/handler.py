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
from minio import Minio

logger = logging.getLogger(__name__)

class ChatterboxHandler(InferenceHandler):
    """Chatterbox TTS model."""

    def __init__(self, model_name: str):
        super().__init__(model_name)

    def _do_load_model(self):
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
            self.state = InferenceStatus.COMPLETED
            total_time = time.time() - self.loading_start_time
            logger.info(f"==== Model loaded successfully and ready for inference - Total loading time: {total_time:.2f} seconds ({total_time/60:.2f} minutes) ====")
            
            return InferenceResponse(
                status=InferenceStatus.COMPLETED,
                message="Model is ready to use.",
                data=""
            )

        except Exception as e:
            logger.error(f"Chatterbox TTS model loading failed: {str(e)}")
            self.state = InferenceStatus.FAILED
            self.error_message = str(e)
            return InferenceResponse(
                status=InferenceStatus.ERROR,
                message=f"Failed to load model: {str(e)}",
                data=""
            )

    def is_loaded(self):
        """Check if model is loaded."""
        return self.model is not None
    
    def infer(self, request_data: Dict[str, Any]) -> bytes:
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
                
                client = Minio(
                    endpoint=settings.MINIO_ENDPOINT_URL,
                    access_key=settings.MINIO_ACCESS_KEY,
                    secret_key=settings.MINIO_SECRET_KEY,
                    secure=True,
                    cert_check=False
                )

                bucket_exists = client.bucket_exists(settings.MINIO_BUCKET_NAME)
                
                if not bucket_exists:
                    client.make_bucket(settings.MINIO_BUCKET_NAME)
                
                bucket_name = settings.MINIO_BUCKET_NAME
                
                audio_filename = f"{uuid4()}.wav"
                
                buffer_size = buffer.getbuffer().nbytes
                
                logger.info(f"==== Uploading to MinIO: {bucket_name}/{audio_filename} ====")
                client.put_object(
                    bucket_name,
                    audio_filename,
                    buffer,
                    buffer_size,
                    content_type="audio/wav"
                )

                base_url = settings.MINIO_ENDPOINT_URL
                
                audio_url = f"https://{base_url}/{bucket_name}/{audio_filename}"
                logger.info(f"==== Audio uploaded to MinIO: {audio_url} ====")
                
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
