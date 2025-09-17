from fastapi import APIRouter, UploadFile, File, HTTPException
from . import service
from . import schemas

router = APIRouter()


@router.post("", response_model=schemas.AudioUploadResponse)
async def upload_audio_endpoint(file: UploadFile = File(...)):
    """
    Endpoint for uploading an audio file.
    
    Args:
        file: The audio file to upload
        
    Returns:
        Information about the uploaded audio, including the URL to access it
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate that the file is an audio file
    content_type = file.content_type
    if not content_type or not content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400,
            detail=f"File must be an audio file, not {content_type}"
        )
    
    try:
        result = await service.save_upload_file(file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving audio: {str(e)}")
