"""Router for image upload endpoints.

This module defines the API endpoints for handling image uploads.
It validates incoming image files and delegates processing to the service layer.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from . import service
from . import schemas

# Create router for this feature
router = APIRouter()


@router.post("", response_model=schemas.ImageUploadResponse)
async def upload_image_endpoint(file: UploadFile = File(...)):
    """
    Upload an image file endpoint.
    
    This endpoint handles image file uploads, validates that the uploaded file is
    actually an image by checking its MIME type, and then processes the upload
    through the image upload service.
    
    Args:
        file (UploadFile): The image file to upload, provided as a form field
        
    Returns:
        schemas.ImageUploadResponse: Information about the uploaded image, including:
            - filename: Unique generated filename
            - content_type: MIME type of the image
            - image_url: URL where the image can be accessed
            - size: File size in bytes
            
    Raises:
        HTTPException(400): If no file is provided or the file is not an image
        HTTPException(500): If there's an error saving the image
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate that the file is an image
    content_type = file.content_type
    if not content_type or not content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"File must be an image, not {content_type}"
        )
    
    try:
        result = await service.save_upload_file(file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")
