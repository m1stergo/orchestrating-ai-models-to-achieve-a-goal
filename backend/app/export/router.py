from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from . import service
from . import schemas

router = APIRouter()


@router.post("/{product_id}", response_model=schemas.ExportResponse)
async def export_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    """
    Export single product data as a ZIP file.
    
    Creates a ZIP file containing:
    - product.csv: Product data in CSV format
    - images/: Product images
    - audio/: Product audio file
    
    Args:
        product_id: ID of the product to export
    
    Returns:
        Information about the generated export file including download URL
    """
    try:
        result = await service.create_export_zip(db, product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating export: {str(e)}")
