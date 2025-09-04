#!/usr/bin/env python3
"""
Script para sincronizar modelos con RunPod S3 storage.
Permite subir y descargar modelos desde el Network Volume S3.
"""

import os
import sys
import boto3
import logging
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class S3ModelSync:
    """Maneja la sincronización de modelos con RunPod S3 storage."""
    
    def __init__(self):
        self.s3_client = None
        self._setup_s3_client()
    
    def _setup_s3_client(self):
        """Configura el cliente S3 con las credenciales de RunPod."""
        try:
            if not all([settings.S3_ENDPOINT_URL, settings.S3_BUCKET_NAME, settings.S3_REGION]):
                logger.warning("S3 configuration incomplete. Using local storage only.")
                return
            
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                region_name=settings.S3_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            
            # Test connection
            self.s3_client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
            logger.info(f"S3 connection established to {settings.S3_BUCKET_NAME}")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
            self.s3_client = None
        except ClientError as e:
            logger.error(f"S3 connection failed: {e}")
            self.s3_client = None
        except Exception as e:
            logger.error(f"Unexpected error setting up S3: {e}")
            self.s3_client = None
    
    def upload_model(self, local_model_dir: str, s3_prefix: str = "models/"):
        """
        Sube el modelo local al S3 storage.
        
        Args:
            local_model_dir: Directorio local del modelo
            s3_prefix: Prefijo en S3 (carpeta)
        """
        if not self.s3_client:
            logger.error("S3 client not available")
            return False
        
        local_path = Path(local_model_dir)
        if not local_path.exists():
            logger.error(f"Local model directory not found: {local_path}")
            return False
        
        try:
            logger.info(f"Uploading model from {local_path} to S3...")
            
            # Upload all files recursively
            for file_path in local_path.rglob('*'):
                if file_path.is_file():
                    # Calculate relative path for S3 key
                    relative_path = file_path.relative_to(local_path.parent)
                    s3_key = f"{s3_prefix}{relative_path}".replace('\\', '/')
                    
                    logger.info(f"Uploading {file_path} -> s3://{settings.S3_BUCKET_NAME}/{s3_key}")
                    
                    self.s3_client.upload_file(
                        str(file_path),
                        settings.S3_BUCKET_NAME,
                        s3_key
                    )
            
            logger.info("Model upload completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading model: {e}")
            return False
    
    def download_model(self, s3_prefix: str = "models/", local_model_dir: str = "./models"):
        """
        Descarga el modelo desde S3 al directorio local.
        
        Args:
            s3_prefix: Prefijo en S3 (carpeta)
            local_model_dir: Directorio local donde guardar
        """
        if not self.s3_client:
            logger.error("S3 client not available")
            return False
        
        local_path = Path(local_model_dir)
        local_path.mkdir(parents=True, exist_ok=True)
        
        try:
            logger.info(f"Downloading model from S3 to {local_path}...")
            
            # List all objects with the prefix
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=settings.S3_BUCKET_NAME, Prefix=s3_prefix)
            
            file_count = 0
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        s3_key = obj['Key']
                        
                        # Skip directories
                        if s3_key.endswith('/'):
                            continue
                        
                        # Calculate local file path
                        relative_path = s3_key[len(s3_prefix):]
                        local_file_path = local_path / relative_path
                        
                        # Create parent directories
                        local_file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        logger.info(f"Downloading s3://{settings.S3_BUCKET_NAME}/{s3_key} -> {local_file_path}")
                        
                        self.s3_client.download_file(
                            settings.S3_BUCKET_NAME,
                            s3_key,
                            str(local_file_path)
                        )
                        file_count += 1
            
            if file_count > 0:
                logger.info(f"Model download completed successfully ({file_count} files)")
                return True
            else:
                logger.warning("No model files found in S3")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            return False
    
    def model_exists_in_s3(self, s3_prefix: str = "models/") -> bool:
        """Verifica si el modelo existe en S3."""
        if not self.s3_client:
            return False
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=settings.S3_BUCKET_NAME,
                Prefix=s3_prefix,
                MaxKeys=1
            )
            return 'Contents' in response and len(response['Contents']) > 0
        except Exception as e:
            logger.error(f"Error checking model in S3: {e}")
            return False

def main():
    """Función principal para CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync models with RunPod S3 storage")
    parser.add_argument(
        "action",
        choices=["upload", "download", "check"],
        help="Action to perform"
    )
    parser.add_argument(
        "--local-dir",
        default="./models",
        help="Local model directory (default: ./models)"
    )
    parser.add_argument(
        "--s3-prefix",
        default="models/",
        help="S3 prefix/folder (default: models/)"
    )
    
    args = parser.parse_args()
    
    sync = S3ModelSync()
    
    if args.action == "upload":
        success = sync.upload_model(args.local_dir, args.s3_prefix)
        sys.exit(0 if success else 1)
    
    elif args.action == "download":
        success = sync.download_model(args.s3_prefix, args.local_dir)
        sys.exit(0 if success else 1)
    
    elif args.action == "check":
        exists = sync.model_exists_in_s3(args.s3_prefix)
        print(f"Model exists in S3: {exists}")
        sys.exit(0 if exists else 1)

if __name__ == "__main__":
    main()
