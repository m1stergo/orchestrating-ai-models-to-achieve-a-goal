from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from . import service
from . import schemas

router = APIRouter()


@router.post("/", response_model=schemas.ImageUploadResponse)
@router.post("", response_model=schemas.ImageUploadResponse)  # Duplicar ruta para manejar con y sin barra diagonal
async def upload_image_endpoint(file: UploadFile = File(...), request: Request = None):
    """
    Endpoint para subir una imagen.
    
    Args:
        file: El archivo de imagen a subir
        
    Returns:
        Información sobre la imagen subida, incluyendo la URL para acceder a ella
    """
    if not file:
        raise HTTPException(status_code=400, detail="No se ha proporcionado ningún archivo")
    
    # Validar que el archivo es una imagen
    content_type = file.content_type
    if not content_type or not content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"El archivo debe ser una imagen, no {content_type}"
        )
    
    try:
        result = await service.save_upload_file(file, request)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar la imagen: {str(e)}")
