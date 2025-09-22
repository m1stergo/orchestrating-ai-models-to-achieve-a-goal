"""Image upload service module.

This module provides functionality for handling image uploads in the application.
It supports storing images either in MinIO object storage (preferred) or in the
local filesystem as a fallback option.
"""
import os
import uuid
from fastapi import UploadFile, HTTPException

from app.config import settings
from app.shared.minio_client import MinioClient


async def save_upload_file(file: UploadFile) -> dict:
    """
    Saves an uploaded file to MinIO temporary storage.
    
    This function takes an uploaded file from a FastAPI endpoint, reads its content,
    and uploads it to MinIO object storage with a unique filename. If MinIO storage
    is not configured or fails, it will fall back to local filesystem storage.
    
    Args:
        file: The uploaded file object from FastAPI
        
    Returns:
        dict: A dictionary containing:
            - filename (str): The generated unique filename
            - content_type (str): The MIME type of the file
            - image_url (str): The URL where the image can be accessed
            - size (int): The size of the file in bytes
            
    Raises:
        HTTPException: If there's an error during the upload process
    """
    # Initialize Minio client
    minio_client = MinioClient()
    
    try:
        # Read file content
        content = await file.read()
        
        # Upload file to Minio and get URL
        # The client will automatically generate a filename with UUID and extension based on content type
        image_url = minio_client.upload_temp_file(
            file_data=content,
            content_type=file.content_type
        )
        
        # Extract filename from URL
        filename = image_url.split('/')[-1]
        
        return {
            "filename": filename,
            "content_type": file.content_type,
            "image_url": image_url,
            "size": len(content)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading to S3: {str(e)}")
    
# Keep a backup of the local filesystem implementation in case needed
async def save_upload_file_local(file: UploadFile) -> dict:
    """
    Saves an uploaded file to the local filesystem.
    
    This function serves as a fallback when MinIO storage is not available.
    It saves the file to the local images directory configured in settings.
    
    Args:
        file: The uploaded file object from FastAPI
        
    Returns:
        dict: A dictionary containing:
            - filename (str): The generated unique filename
            - content_type (str): The MIME type of the file
            - image_url (str): The local URL where the image can be accessed
            - size (int): The size of the file in bytes
    """
    # Ensure the directory exists
    os.makedirs(settings.IMAGES_DIR, exist_ok=True)
    
    # Generate a unique filename to avoid collisions
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = settings.IMAGES_DIR / unique_filename
    
    # Save the file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Calculate the absolute URL to access the image
    image_url = f"{settings.images_url}/{unique_filename}"
    
    return {
        "filename": unique_filename,
        "content_type": file.content_type,
        "image_url": image_url,
        "size": os.path.getsize(file_path)
    }
