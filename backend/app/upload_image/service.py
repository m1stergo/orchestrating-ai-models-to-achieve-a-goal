import os
import uuid
from fastapi import UploadFile
from pathlib import Path
from starlette.requests import Request

from app.config import settings


async def save_upload_file(file: UploadFile, request: Request = None) -> dict:
    """
    Guarda un archivo subido en el directorio de imágenes.
    
    Args:
        file: El archivo subido
        request: Objeto Request para obtener la URL base (opcional)
        
    Returns:
        Un diccionario con información sobre el archivo guardado
    """
    # Asegurarse de que el directorio existe
    os.makedirs(settings.IMAGES_DIR, exist_ok=True)
    
    # Generar un nombre de archivo único para evitar colisiones
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = settings.IMAGES_DIR / unique_filename
    
    # Guardar el archivo
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Calcular la URL absoluta para acceder a la imagen
    # Usar settings.images_url que puede ser local o CDN/cloud storage
    image_url = f"{settings.images_url}/{unique_filename}"
    
    return {
        "filename": unique_filename,
        "content_type": file.content_type,
        "image_url": image_url,
        "size": os.path.getsize(file_path)
    }
