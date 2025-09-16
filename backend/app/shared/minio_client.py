"""
Minio client utility for S3-compatible storage operations.
"""
import io
import uuid
import logging
from typing import Optional, BinaryIO, Union, Tuple

from minio import Minio
from minio.error import S3Error

from app.config import settings

logger = logging.getLogger(__name__)

class MinioClient:
    """
    Simplified client for interacting with Minio S3-compatible storage.
    """
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to avoid multiple client instances."""
        if cls._instance is None:
            cls._instance = super(MinioClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the Minio client if not already initialized."""
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT_URL,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
            cert_check=False  # Necesario para algunos servidores con certificados autofirmados
        )
        
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.temp_prefix = settings.MINIO_TEMP_PREFIX
        
        # Ensure bucket exists
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"===== Created bucket: {self.bucket_name} =====")
        except S3Error as e:
            logger.error(f"===== Error ensuring bucket {self.bucket_name} exists: {e} =====")
        
        self._initialized = True
        logger.info(f"===== Minio client initialized with endpoint: {settings.MINIO_ENDPOINT_URL} =====")
    
    def upload_file(self, file_data: Union[bytes, BinaryIO], filename: Optional[str] = None, 
                  content_type: Optional[str] = None) -> str:
        """
        Upload a file to Minio storage and return the URL.
        
        Args:
            file_data: File content as bytes or file-like object
            filename: Optional filename (will generate UUID if not provided)
            content_type: MIME type of the file
            
        Returns:
            URL to access the uploaded file
        """
        try:
            # Generate filename with UUID if not provided
            if not filename:
                ext = '.bin'
                if content_type:
                    if 'image/' in content_type:
                        if 'jpeg' in content_type:
                            ext = '.jpg'
                        elif 'webp' in content_type:
                            ext = '.webp'
                        else:
                            ext = '.png'
                    elif 'audio/' in content_type:
                        ext = '.wav' if 'wav' in content_type else '.mp3'
                filename = f"{uuid.uuid4()}{ext}"
            
            # Add temp prefix if needed
            if self.temp_prefix and not filename.startswith(self.temp_prefix):
                object_name = f"{self.temp_prefix}{filename}"
            else:
                object_name = filename
                
            # Convert to BytesIO if bytes are provided
            if isinstance(file_data, bytes):
                file_obj = io.BytesIO(file_data)
                file_size = len(file_data)
            else:
                # Assume it's a file-like object
                file_obj = file_data
                file_obj.seek(0, io.SEEK_END)
                file_size = file_obj.tell()
                file_obj.seek(0)
            
            # Upload file
            logger.info(f"===== Uploading to MinIO: {self.bucket_name}/{object_name}")
            self.client.put_object(
                self.bucket_name,
                object_name,
                file_obj,
                file_size,
                content_type=content_type
            )
            
            # Generate URL
            base_url = settings.MINIO_PUBLIC_URL or f"https://{settings.MINIO_ENDPOINT}"
            url = f"{base_url}/{self.bucket_name}/{object_name}"
            
            logger.info(f"===== File uploaded to MinIO: {url} =====")
            return url
            
        except Exception as e:
            error_msg = f"===== Error uploading to MinIO: {str(e)} ====="
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def upload_temp_file(self, file_data: Union[bytes, BinaryIO], 
                       content_type: Optional[str] = None) -> str:
        """
        Upload a file to the temporary folder with an auto-generated filename.
        
        Args:
            file_data: File content as bytes or file-like object
            content_type: MIME type of the file
            
        Returns:
            URL to access the uploaded file
        """
        return self.upload_file(file_data=file_data, content_type=content_type)
