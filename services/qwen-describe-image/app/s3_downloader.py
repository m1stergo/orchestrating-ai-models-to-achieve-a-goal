"""
S3 Model Downloader for RunPod Serverless
Downloads model files from RunPod S3 storage to local cache.
"""
import os
import logging
from pathlib import Path
from typing import Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from .config import settings

logger = logging.getLogger(__name__)


class S3ModelDownloader:
    """Downloads model files from S3 to local cache."""
    
    def __init__(self):
        self.s3_client = None
        self._initialize_s3_client()
    
    def _initialize_s3_client(self) -> None:
        """Initialize S3 client with RunPod credentials."""
        if not all([
            settings.S3_ENDPOINT,
            settings.S3_BUCKET,
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY
        ]):
            logger.warning("S3 credentials not configured. S3 download will be skipped.")
            return
        
        try:
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name="us-east-1"  # RunPod default
            )
            logger.info(f"S3 client initialized for endpoint: {settings.S3_ENDPOINT}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.s3_client = None
    
    def is_model_cached_locally(self) -> bool:
        """Check if model is already cached locally."""
        local_path = Path(settings.LOCAL_MODEL_DIR)
        ready_file = local_path / ".ready"
        
        if ready_file.exists():
            logger.info(f"Model found in local cache: {local_path}")
            return True
        
        logger.info(f"Model not found in local cache: {local_path}")
        return False
    
    def ensure_model_local(self) -> Optional[str]:
        """
        Ensure model is available locally.
        Returns local model path if successful, None if failed.
        """
        # Check if already cached
        if self.is_model_cached_locally():
            return settings.LOCAL_MODEL_DIR
        
        # If no S3 client, can't download
        if not self.s3_client:
            logger.warning("No S3 client available for model download")
            return None
        
        # Download from S3
        return self._download_model_from_s3()
    
    def _download_model_from_s3(self) -> Optional[str]:
        """Download model files from S3 to local cache."""
        local_path = Path(settings.LOCAL_MODEL_DIR)
        local_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Downloading model from S3 bucket: {settings.S3_BUCKET}")
        logger.info(f"S3 prefix: {settings.MODEL_PREFIX}")
        logger.info(f"Local destination: {local_path}")
        
        try:
            # List all objects under the model prefix
            paginator = self.s3_client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(
                Bucket=settings.S3_BUCKET,
                Prefix=settings.MODEL_PREFIX
            )
            
            downloaded_files = 0
            total_size = 0
            
            for page in page_iterator:
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    size = obj["Size"]
                    
                    # Skip directory markers
                    if key.endswith("/"):
                        continue
                    
                    # Calculate relative path
                    relative_path = key[len(settings.MODEL_PREFIX):]
                    if not relative_path:  # Skip if empty after removing prefix
                        continue
                    
                    dest_file = local_path / relative_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Download only if file doesn't exist or size differs
                    if not dest_file.exists() or dest_file.stat().st_size != size:
                        logger.info(f"Downloading: {key} -> {dest_file}")
                        self.s3_client.download_file(
                            settings.S3_BUCKET,
                            key,
                            str(dest_file)
                        )
                        downloaded_files += 1
                        total_size += size
                    else:
                        logger.debug(f"Skipping existing file: {dest_file}")
            
            # Mark as ready
            ready_file = local_path / ".ready"
            ready_file.write_text("Model download completed successfully")
            
            logger.info(f"Model download completed: {downloaded_files} files, {total_size / (1024**3):.2f} GB")
            return str(local_path)
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                logger.error(f"S3 bucket not found: {settings.S3_BUCKET}")
            elif error_code == 'AccessDenied':
                logger.error("S3 access denied. Check credentials and permissions.")
            else:
                logger.error(f"S3 client error: {e}")
            return None
        except NoCredentialsError:
            logger.error("S3 credentials not found or invalid")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during S3 download: {e}")
            return None


# Global instance
s3_downloader = S3ModelDownloader()
