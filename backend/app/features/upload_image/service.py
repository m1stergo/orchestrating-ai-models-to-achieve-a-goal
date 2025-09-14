import os
import uuid
from fastapi import UploadFile, HTTPException

from app.config import settings
from app.shared.minio_client import MinioClient


async def save_upload_file(file: UploadFile) -> dict:
    """
    Saves an uploaded file to Minio temporary storage.
    
    Args:
        file: The uploaded file
        
    Returns:
        A dictionary with information about the saved file
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
    Saves an uploaded file to the local images directory.
    
    Args:
        file: The uploaded file
        
    Returns:
        A dictionary with information about the saved file
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
