import os
import uuid
from fastapi import UploadFile

from app.config import settings


async def save_upload_file(file: UploadFile) -> dict:
    """
    Saves an uploaded file to the images directory.
    
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
    # Use settings.images_url which can be local or CDN/cloud storage
    image_url = f"{settings.images_url}/{unique_filename}"
    
    return {
        "filename": unique_filename,
        "content_type": file.content_type,
        "image_url": image_url,
        "size": os.path.getsize(file_path)
    }
