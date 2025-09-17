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
        
        self.bucket_name = settings.MINIO_PUBLIC_BUCKET
        self.temp_bucket_name = settings.MINIO_TEMP_BUCKET
        
        # Ensure buckets exist
        for bucket in [self.bucket_name, self.temp_bucket_name]:
            try:
                if bucket and not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info(f"===== Created bucket: {bucket} =====")
            except S3Error as e:
                logger.error(f"===== Error ensuring bucket {bucket} exists: {e} =====")
        
        self._initialized = True
        logger.info(f"===== Minio client initialized with endpoint: {settings.MINIO_ENDPOINT_URL} =====")
    
    def upload_file(self, file_data: Union[bytes, BinaryIO], filename: Optional[str] = None, 
                  content_type: Optional[str] = None) -> str:
        """
        Upload a file to the public bucket in Minio storage and return the URL.
        
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
            
            # Use filename as object name
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
            
            # Upload file to the public bucket
            logger.info(f"===== Uploading to MinIO public bucket: {self.bucket_name}/{object_name}")
            self.client.put_object(
                self.bucket_name,  # Public bucket
                object_name,
                file_obj,
                file_size,
                content_type=content_type
            )
            
            # Generate URL
            base_url = settings.MINIO_PUBLIC_URL or f"https://{settings.MINIO_ENDPOINT_URL}"
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
        Upload a file to the temporary bucket with an auto-generated filename.
        
        Args:
            file_data: File content as bytes or file-like object
            content_type: MIME type of the file
            
        Returns:
            URL to access the uploaded file
        """
        try:
            # Generate filename with UUID
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
            
            # Upload file to temp bucket
            logger.info(f"===== Uploading to MinIO temp bucket: {self.temp_bucket_name}/{filename}")
            self.client.put_object(
                self.temp_bucket_name,  # Temp bucket
                filename,
                file_obj,
                file_size,
                content_type=content_type
            )
            
            # Generate URL
            base_url = settings.MINIO_PUBLIC_URL or f"https://{settings.MINIO_ENDPOINT_URL}"
            url = f"{base_url}/{self.temp_bucket_name}/{filename}"
            
            logger.info(f"===== File uploaded to MinIO temp: {url} ======")
            return url
            
        except Exception as e:
            error_msg = f"===== Error uploading to MinIO temp bucket: {str(e)} ======"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
