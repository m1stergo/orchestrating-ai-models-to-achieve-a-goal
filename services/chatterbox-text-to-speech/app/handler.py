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
from app.minio_client import MinioClient
minio_client = MinioClient()

logger = logging.getLogger(__name__)

class ChatterboxHandler(InferenceHandler):
    """Chatterbox TTS model."""

    def __init__(self, model_name: str):
        super().__init__(model_name)

    def _materialize_model(self) -> str:
        # Usar la configuración centralizada de Pydantic
        base_models_dir = settings.MODELS_DIR
        local_dir = f"{base_models_dir}/{self.model_name.replace('/', '__')}"
        os.makedirs(local_dir, exist_ok=True)
        cache_dir = settings.HUGGINGFACE_CACHE_DIR
        logger.info(f"==== snapshot_download to {local_dir} (cache: {cache_dir}) ====")
        path = snapshot_download(
            repo_id=self.model_name,
            cache_dir=cache_dir,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
            allow_patterns=["*.safetensors","*.bin","*.json","tokenizer.*","processor.*","*.model","vocab.*","merges.txt",".gitattributes"],
            ignore_patterns=["images/*","assets/*","examples/*","docs/*","test*/*","*.md"],
        )
        return path

    def _do_load_model(self):
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
                self.model = ChatterboxTTS.from_pretrained(
                    local_repo, **model_kwargs
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
